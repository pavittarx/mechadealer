from urllib.parse import urlparse, parse_qs, urlencode
from coreutils import Logger, CredentialsManager
from datetime import datetime

import http.server
import socketserver
import threading
import requests
import json
import os

log = Logger("orders_management")
logger = log.get_logger()
credsStore = CredentialsManager()


CLIENT_ID = os.getenv("UPSTOX_CLIENT_ID")
CLIENT_SECRET = os.getenv("UPSTOX_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8900/callback"
PORT = 8900
AUTH_URL = "https://api-v2.upstox.com/login/authorization/dialog"
TOKEN_URL = "https://api-v2.upstox.com/login/authorization/token"

httpd_server = None


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
                credsStore.set_credential("upstox.auth_code", authorization_code)

            else:
                logger.error(
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
    auth_code = credsStore.get_credential("upstox.auth_code")

    if not auth_code:
        logger.error(
            "[Upstox:Auth] Authorization code not available. Cannot fetch access token."
        )
        return
    logger.info("[Upstox:Auth] Exchanging authorization code for access token.")

    headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "code": auth_code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    try:
        response = requests.post(TOKEN_URL, headers=headers, data=data)
        response.raise_for_status()

        token_data = response.json()
        access_token = token_data.get("access_token")

        if access_token:
            logger.info("[Upstox:Auth] Access token obtained successfully.")
            return access_token

        else:
            logger.error("[Upstox:Auth] Access token not found in the response.")
            logger.error(json.dumps(response.json()))

    except requests.exceptions.RequestException as e:
        logger.error(
            f"[Upstox:Auth] Error occurred while requesting the access token: {e}"
        )
        if e.response:
            logger.error(f"(Exception) Response Body: {e.response.text}")


def authorize():
    global httpd_server

    logger.info(f"[Upstox:Auth] Starting local server on port {PORT}...")
    socketserver.TCPServer.allow_reuse_address = True
    httpd_server = socketserver.TCPServer(("", PORT), AuthHandler)

    auth_params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
    }
    login_url = f"{AUTH_URL}?{urlencode(auth_params)}"
    logger.info(
        f"[Upstox:Auth] Please open the following URL in your browser:\n\n{login_url}\n\n"
    )

    logger.info("[Upstox:Auth] Waiting for user authorization in the browser...")
    httpd_server.serve_forever()

    logger.info("[Upstox:Auth] Server has been shut down.")
    token = get_access_token()

    if not token:
        logger.error("[Upstox:Auth] Failed to obtain access token.")
        return

    credsStore.set_credential("upstox.token", token)
    credsStore.set_credential("upstox.last_fetched", datetime.now().isoformat())
