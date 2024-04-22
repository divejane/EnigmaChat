import socket
from threading import Thread, Event

working_sock = []
stop = Event()


def punch_send(peer_ip: str, peer_port: int) -> object:
    hp_send_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while not stop.is_set():
        try:
            hp_send_sock.connect((peer_ip, peer_port))
        except ConnectionRefusedError:
            print('restarting connection...')
            continue
        stop.set()
        working_sock.append(hp_send_sock)


def punch_recv(sock: object, peer_ip: str, peer_port: int) -> object:
    punch_send_thr = Thread(
        target=punch_send, args=(peer_ip, peer_port), daemon=True)
    punch_send_thr.start()
    sock.listen()
    while not stop.is_set():
        try:
            conn, addr = sock.accept()
        except socket.timeout:
            print('restarting listener...')
            continue
        stop.set()
        working_sock.append(conn)
    return working_sock[0]
