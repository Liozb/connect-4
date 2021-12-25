import socket
from globals_var import *


# Opening Client socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Connecting to server's socket
client_socket.connect((HOST, PORT))


def await_sever(conn, buffer=1024):
    """
    main function of client
    :param conn: connection to server's socket
    :param buffer: buffer for message receiving
    """
    while True:
        raw_res = conn.recv(buffer).decode(FORMAT)
        func, q = raw_res.split(SEP)
        print(q)
        if func == "None":
            func = None
        if func is not None and func != "100":
            choice = input()
            conn.send(f"{func}{SEP}{choice}".encode(FORMAT))
        elif func is None:
            break


await_sever(client_socket)

