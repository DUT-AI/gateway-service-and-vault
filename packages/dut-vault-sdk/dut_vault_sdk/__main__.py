import argparse
import os
import subprocess
import sys

from dut_vault_sdk.client import VaultClient


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="dut-vault",
        description="Centralized Vault CLI Runner - Zero disk artifacts, in-memory secret injection",
    )
    subparsers = parser.add_subparsers(dest="subcommand", required=True)

    run_parser = subparsers.add_parser(
        "run", help="Run a command with secrets injected into RAM"
    )
    run_parser.add_argument("--project", "-p", required=True, help="Target project ID")
    run_parser.add_argument(
        "--scope", "-s", default=None, help="Secret scope to load (default: all)"
    )
    run_parser.add_argument(
        "--role", "-r", default="user", help="Client user role header"
    )
    run_parser.add_argument(
        "--api-url",
        default=os.environ.get("DUT_VAULT_URL", "http://localhost:8000"),
        help="Central Control Plane API URL",
    )
    run_parser.add_argument(
        "--no-watch",
        action="store_true",
        help="Disable background SSE live-reload listener",
    )
    run_parser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help="Command to execute (after '--')",
    )

    args = parser.parse_args()

    cmd = args.command
    if cmd and cmd[0] == "--":
        cmd = cmd[1:]

    if not cmd:
        print(
            "Error: No command specified to run. Usage: dut-vault run --project <ID> -- <CMD>",
            file=sys.stderr,
        )
        sys.exit(1)

    client = VaultClient(
        base_url=args.api_url,
        project_id=args.project,
        user_role=args.role,
        scope=args.scope,
        inject_environ=True,
        auto_reconnect=not args.no_watch,
    )

    if args.no_watch:
        client.fetch_secrets()
    else:
        client.connect(wait_for_stream=False)

    try:
        proc = subprocess.run(cmd, check=False, env=os.environ)
        sys.exit(proc.returncode)
    except KeyboardInterrupt:
        sys.exit(130)
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()
