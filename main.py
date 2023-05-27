import socket

HOST = "127.0.0.1"
PORT = 9000

# a static response to serve to clients
RESPONSE = b"""\
HTTP/1.1 200 OK
Content-type: text/html
Content-length: 15

<h1>Hello!</h1>""".replace(b"\n", b"\r\n")

# By default, socket.socket creates TCP sockets.
with socket.socket() as server_sock:
    # This tells the kernel to reuse sockets that are in `TIME_WAIT` state.
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # This tells the socket what address to bind to.
    server_sock.bind((HOST, PORT))

    # 0 is the number of pending connections the socket may have before
    # new connections are refused.  Since this server is going to process
    # one connection at a time, we want to refuse any additional connections.
    server_sock.listen(0)
    print(f"Listening on {HOST}:{PORT}...")

    while True:
        # wait for connections
        client_sock, client_addr = server_sock.accept()
        print(f"New connection from {client_addr}.")

        # send pre-defined response to the newly connected client
        with client_sock:
            client_sock.sendall(RESPONSE)
