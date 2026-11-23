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
            default = "http://host.docker.internal:8000/api/v1/gateway/verify-binding",
        },
    },
}

local _M = {
    version = 0.2,
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
    if not virtual_key or virtual_key == "" then
        core.log.warn("Missing X-Virtual-Key header")
        return 401, { error = "UNAUTHORIZED", message = "Missing X-Virtual-Key header" }
    end

    -- 2. Extract client certificate SHA-256 fingerprint from mTLS termination
    local cert_fingerprint = ngx.var.ssl_client_fingerprint
    local client_raw_cert = ngx.var.ssl_client_raw_cert or ngx.var.ssl_client_cert
    if (not cert_fingerprint or cert_fingerprint == "") and (not client_raw_cert or client_raw_cert == "") then
        core.log.warn("Client did not present a valid mTLS certificate")
        return 403, { error = "MTLS_REQUIRED", message = "Valid client certificate required" }
    end

    -- 3. Extract requested project ID from header
    local project_id = core.request.header(ctx, "X-Project-Id") or "default"

    -- 4. Extract requested service slug from uri (e.g. /services/{service_slug}/*)
    local service_slug = string.match(ngx.var.uri or "", "^/services/([^/]+)")

    -- 5. Verify Identity Binding with Control Plane
    local control_plane_url = conf.control_plane_url or "http://host.docker.internal:8000/api/v1/gateway/verify-binding"
    local httpc = http.new()
    httpc:set_timeout(2000) -- 2s timeout for fail-closed safety

    local res, err = httpc:request_uri(control_plane_url, {
        method = "POST",
        headers = {
            ["Content-Type"] = "application/json",
        },
        body = core.json.encode({
            raw_virtual_key = virtual_key,
            cert_fingerprint = cert_fingerprint or "",
            client_raw_cert = client_raw_cert,
            project_id = project_id,
            service_slug = service_slug,
        }),
    })

    if not res or res.status ~= 200 then
        core.log.warn("Identity binding check failed: ", err or (res and res.body))
        local detail = "Virtual Access Key is not bound to this client certificate, project, or service"
        local status_code = (res and res.status == 429) and 429 or 403
        if res and res.body then
            local decoded = core.json.decode(res.body)
            if decoded then
                detail = decoded.message or decoded.detail or detail
            end
        end
        return status_code, {
            error = (status_code == 429) and "DAILY_QUOTA_EXCEEDED" or "IDENTITY_MISMATCH",
            message = detail,
        }
    end

    -- Success: Identity binding verified. Virtual Key is retained for downstream rate limiting (limit-count),
    -- and will be removed by proxy-rewrite before forwarding to the upstream service.
    return
end

return _M
