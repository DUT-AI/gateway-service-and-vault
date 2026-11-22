-- Apache APISIX Custom Lua Plugin: identity-binding-filter
-- Enforces cryptographic binding between Virtual Access Key and mTLS Client Certificate

local core = require("apisix.core")
local http = require("resty.http")

local plugin_name = "identity-binding-filter"

local schema = {
    type = "object",
    properties = {
        control_plane_url = {
            type = "string",
            default = "http://api:8000/api/v1/gateway/verify-binding",
        },
    },
}

local _M = {
    version = 0.1,
    priority = 2500, -- High priority: runs before proxy-rewrite and upstream dispatch
    name = plugin_name,
    schema = schema,
}

function _M.check_schema(conf)
    return core.schema.check(schema, conf)
end

function _M.rewrite(conf, ctx)
    -- 1. Extract Virtual Access Key from header
    local virtual_key = core.request.header(ctx, "X-Virtual-Key")
    if not virtual_key then
        core.log.error("Missing X-Virtual-Key header")
        return 401, { error = "UNAUTHORIZED", message = "Missing X-Virtual-Key header" }
    end

    -- 2. Extract client certificate SHA-256 fingerprint from mTLS termination
    local cert_fingerprint = ngx.var.ssl_client_fingerprint
    if not cert_fingerprint or cert_fingerprint == "" then
        core.log.error("Client did not present a valid mTLS certificate")
        return 403, { error = "MTLS_REQUIRED", message = "Valid client certificate required" }
    end

    -- 3. Extract requested project ID from header or path
    local project_id = core.request.header(ctx, "X-Project-Id") or "default"

    -- 4. Verify Identity Binding with Control Plane cache / endpoint
    local httpc = http.new()
    httpc:set_timeout(2000) -- 2s timeout for fail-closed safety

    local res, err = httpc:request_uri(conf.control_plane_url, {
        method = "POST",
        headers = {
            ["Content-Type"] = "application/json",
        },
        body = core.json.encode({
            raw_virtual_key = virtual_key,
            cert_fingerprint = cert_fingerprint,
            project_id = project_id,
        }),
    })

    if not res or res.status ~= 200 then
        core.log.warn("Identity binding check failed: ", err or (res and res.body))
        return 403, {
            error = "IDENTITY_MISMATCH",
            message = "Virtual Access Key is not bound to this client certificate or project",
        }
    end

    -- Success: Strip virtual key before forwarding
    core.request.set_header(ctx, "X-Virtual-Key", nil)
    return
end

return _M
