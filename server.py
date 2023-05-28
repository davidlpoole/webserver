import mimetypes
import os
import socket

from request import Request
from response import Response

# Where the server should serve files from
SERVER_ROOT = os.path.abspath("www")

HOST = "127.0.0.1"
PORT = 9000


def serve_file(sock: socket.socket, path: str) -> None:
    """Given a socket and the relative path to a file (relative to
    SERVER_SOCK), send that file to the socket if it exists.  If the
    file doesn't exist, send a "404 Not Found" response.
    """
    if path == "/":
        path = "/index.html"

    abspath = os.path.normpath(os.path.join(SERVER_ROOT, path.lstrip("/")))
    if not abspath.startswith(SERVER_ROOT):
        response = Response(status="404 Not Found", content="Not Found")
        response.send(sock)
        return

    try:
        with open(abspath, "rb") as f:
            stat = os.fstat(f.fileno())
            content_type, encoding = mimetypes.guess_type(abspath)
            if content_type is None:
                content_type = "application/octet-stream"

            if encoding is not None:
                content_type += f"; charset={encoding}"

            response = Response(status="200 OK", body=f)
            response.headers.add("content-type", content_type)
            response.send(sock)
            return

    except FileNotFoundError:
        response = Response(status="404 Not Found", content="Not Found")
        response.send(sock)
        return


# By default, socket.socket creates TCP sockets.
with socket.socket() as server_sock:
    # This tells the kernel to reuse sockets that are in `TIME_WAIT` state.
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # This tells the socket what address to bind to.
    server_sock.bind((HOST, PORT))

    # open a listening socket that the server uses to accept new connections.
    # the backlog parameter is the number of pending connections the socket
    # may have before new connections are refused.
    server_sock.listen(0)
    print(f"Listening on {HOST}:{PORT}...")

    while True:
        # Wait for incoming connections.
        # When a client connects, return a new socket object representing the connection
        client_sock, client_addr = server_sock.accept()
        print(f"New connection from {client_addr}.")

        with client_sock:
            try:
                # get the request from the client
                request = Request.from_socket(client_sock)
                print(request)

                # respond to 100-continue status codes for large request bodies
                if "100-continue" in request.headers.get("expect", ""):
                    client_sock.sendall(b"HTTP/1.1 100 Continue\r\n\r\n")

                # get content length header and ensure > 0
                try:
                    content_length = int(request.headers.get("content-length", "0"))
                except ValueError:
                    content_length = 0

                # read body content if content length > 0
                if content_length:
                    body = request.body.read(content_length)
                    print("Request body", body)

                # only allow GET requests
                if request.method != "GET":
                    response = Response(status="405 Method Not Allowed", content="Method Not Allowed")
                    response.send(client_sock)
                    continue

                # find and serve the file
                serve_file(client_sock, request.path)

            except Exception as e:
                print(f"Failed to parse request: {e}")
                response = Response(status="400 Bad Request", content="Bad Request")
                response.send(client_sock)
