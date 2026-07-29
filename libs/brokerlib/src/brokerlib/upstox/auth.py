import http.server
import json
import os
import socketserver
import threading
from datetime import datetime
from urllib.parse import parse_qs, urlencode, urlparse

import requests
from coreutils import CredentialsManager, Logger

REDIRECT_URI = "http://localhost:8900/callback"
PORT = 8900
AUTH_URL = "https://api-v2.upstox.com/login/authorization/dialog"
TOKEN_URL = "https://api-v2.upstox.com/login/authorization/token"

httpd_server = None

_logger = None
_creds_store = None


def get_logger():
    """Build the logger on first use -- constructing one creates a log directory."""
    global _logger

    if _logger is None:
        _logger = Logger("brokerlib.upstox").get_logger()

    return _logger


def get_creds_store() -> CredentialsManager:
    """Build the credentials store on first use -- it touches the filesystem."""
    global _creds_store

    if _creds_store is None:
        _creds_store = CredentialsManager()

    return _creds_store


def get_client_credentials() -> tuple[str, str]:
    """Read and validate the Upstox app credentials from the environment."""
    client_id = os.getenv("UPSTOX_CLIENT_ID")
    client_secret = os.getenv("UPSTOX_CLIENT_SECRET")

    if not client_id:
        raise RuntimeError("UPSTOX_CLIENT_ID is not set in the environment variables.")

    if not client_secret:
        raise RuntimeError(
            "UPSTOX_CLIENT_SECRET is not set in the environment variables."
        )

    return client_id, client_secret


class AuthHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global authorization_code, httpd_server
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)

        if parsed_url.path == "/callback":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            response_html = """
            <html>
            <head>
                <title>Authentication Successful</title>
                <style>
                    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif; text-align: center; padding-top: 50px; background-color: #f0f4f8; }
                    h1 { color: #2c3e50; }
                    p { color: #34495e; }
                </style>
            </head>
            <body>
                <h1>Authentication Successful!</h1>
                <p>You can now close this browser tab and return to your application.</p>
            </body>
            </html>
            """
            self.wfile.write(response_html.encode("utf-8"))

            if "code" in query_params:
                authorization_code = query_params["code"][0]
                get_creds_store().set_credential("upstox.auth_code", authorization_code)

            else:
                get_logger().error(
                    "[Upstox:Auth]: 'code' parameter not found in the callback URL."
                )

            # --- Critical Step: Shut down the server ---
            # The server runs in a separate thread, so it can shut down from here.
            # This ensures the server closes immediately after handling the redirect.
            if httpd_server:
                print("[*] Shutting down the local server...")
                # Shutdown must be run in a separate thread to avoid deadlock
                shutdown_thread = threading.Thread(target=httpd_server.shutdown)
                shutdown_thread.daemon = True
                shutdown_thread.start()
        else:
            self.send_response(404)
            self.end_headers()


def get_access_token():
    auth_code = get_creds_store().get_credential("upstox.auth_code")

    if not auth_code:
        get_logger().error(
            "[Upstox:Auth] Authorization code not available. Cannot fetch access token."
        )
        return
    get_logger().info("[Upstox:Auth] Exchanging authorization code for access token.")

    client_id, client_secret = get_client_credentials()

    headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "code": auth_code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    try:
        response = requests.post(TOKEN_URL, headers=headers, data=data)
        response.raise_for_status()

        token_data = response.json()
        access_token = token_data.get("access_token")

        if access_token:
            get_logger().info("[Upstox:Auth] Access token obtained successfully.")
            return access_token

        else:
            get_logger().error("[Upstox:Auth] Access token not found in the response.")
            get_logger().error(json.dumps(response.json()))

    except requests.exceptions.RequestException as e:
        get_logger().error(
            f"[Upstox:Auth] Error occurred while requesting the access token: {e}"
        )
        if e.response:
            get_logger().error(f"(Exception) Response Body: {e.response.text}")


def authorize():
    global httpd_server

    get_logger().info(f"[Upstox:Auth] Starting local server on port {PORT}...")
    socketserver.TCPServer.allow_reuse_address = True
    httpd_server = socketserver.TCPServer(("", PORT), AuthHandler)

    client_id, _ = get_client_credentials()

    auth_params = {
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
    }
    login_url = f"{AUTH_URL}?{urlencode(auth_params)}"
    get_logger().info(
        f"[Upstox:Auth] Please open the following URL in your browser:\n\n{login_url}\n\n"
    )

    get_logger().info("[Upstox:Auth] Waiting for user authorization in the browser...")
    httpd_server.serve_forever()

    get_logger().info("[Upstox:Auth] Server has been shut down.")
    token = get_access_token()

    if not token:
        get_logger().error("[Upstox:Auth] Failed to obtain access token.")
        return

    get_creds_store().set_credential("upstox.token", token)
    get_creds_store().set_credential("upstox.last_fetched", datetime.now().isoformat())
