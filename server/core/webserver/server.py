import logging
from http.server import (
    ThreadingHTTPServer,
    BaseHTTPRequestHandler
)

from typing import Any
from urllib.parse import urlsplit

from .app import App
from .di import call_with_injection
from .request import Request
from .response import Response

from .exceptions import HTTPException


def _to_response(result: Any) -> Response:
    if isinstance(result, Response):
        return result
    
    if result is None:
        return Response(status_code=200, body=b"", headers={})
    
    if isinstance(result, tuple) and len(result) == 2:
        status, data = result
        return Response.json(data, status_code=int(status))
    
    if isinstance(result, (dict, list)):
        return Response.json(result)
    
    if isinstance(result, bytes):
        return Response(status_code=200, body=result, headers={"content-type": "application/octet-stream"})
    
    return Response.text(str(result))


class WebServer:
    def __init__(self, *, host: str, port: int):
        self.host = host
        self.port = int(port)
        self._logger = logging.getLogger(self.__class__.__name__)

    def run(self, app: App) -> None:
        server = ThreadingHTTPServer((self.host, self.port), self._make_handler(app))
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            self._logger.info("Shutting down webserver...")
        finally:
            server.server_close()

    def _make_handler(self, app: App):
        outer = self

        class Handler(BaseHTTPRequestHandler):
            server_version = "core-webserver/0.1"

            def log_message(self, format: str, *args: Any) -> None:
                outer._logger.info("%s - %s", self.address_string(), format % args)

            def do_GET(self) -> None:
                self._handle("GET")

            def do_POST(self) -> None:
                self._handle("POST")

            def do_PUT(self) -> None:
                self._handle("PUT")

            def _handle(self, method: str) -> None:
                try:
                    resp = self._dispatch(method)
                
                except HTTPException as e:
                    resp = Response.json({"detail": e.detail}, status_code=e.status_code)
                
                except Exception as e:
                    outer._logger.exception("Unhandled error: %s", e)
                    resp = Response.json({"detail": "Internal Server Error"}, status_code=500)

                self.send_response(resp.status_code)
                headers = {k.lower(): v for k, v in (resp.headers or {}).items()}
                if "content-length" not in headers:
                    headers["content-length"] = str(len(resp.body or b""))
                
                for k, v in headers.items():
                    self.send_header(k, v)
                
                self.end_headers()
                if resp.body:
                    self.wfile.write(resp.body)

            def _dispatch(self, method: str) -> Response:
                split = urlsplit(self.path)
                path = split.path or "/"
                query = split.query or ""

                if path != "/" and path.endswith("/"):
                    path = path[:-1]

                # Body
                length = int(self.headers.get("content-length", "0") or "0")
                body = self.rfile.read(length) if length > 0 else b""

                # Match route
                for route in app.router.routes:
                    path_params = route.match(method, path)
                    if path_params is None:
                        continue

                    req = Request(
                        method=method,
                        path=path,
                        raw_path=self.path,
                        headers={k.lower(): v for k, v in self.headers.items()},
                        query_string=query,
                        body=body,
                        client=self.client_address,
                        path_params=path_params,
                        app=app,
                    )

                    result = call_with_injection(route.endpoint, request=req, app=app, dependency_cache={})
                    return _to_response(result)

                raise HTTPException(404, "Not Found")

        return Handler


