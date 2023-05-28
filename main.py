import socket
import typing

HOST = "127.0.0.1"
PORT = 9000

# a static response to serve to clients
RESPONSE = b"""\
HTTP/1.1 200 OK
Content-type: text/html
Content-length: 15

<h1>Hello!</h1>""".replace(b"\n", b"\r\n")


def iter_lines(sock: socket.socket, bufsize: int = 16_384) -> typing.Generator[bytes, None, bytes]:
    """Given a socket, read all the individual CRLF-separated lines
    and yield each one until an empty one is found.  Returns the
    remainder after the empty line.
    """
    buff = b""
    while True:
        data = sock.recv(bufsize)
        if not data:
            return b""

        buff += data
        while True:
            try:
                i = buff.index(b"\r\n")
                line, buff = buff[:i], buff[i + 2:]
                if not line:
                    return buff

                yield line
            except IndexError:
                break


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
            # print the request we get from the client
            for request_line in iter_lines(client_sock):
                print(request_line)

            # send pre-defined response to the client
            client_sock.sendall(RESPONSE)
