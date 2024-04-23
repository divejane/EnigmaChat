import socket
from threading import Thread, Event

working_sock = []
stop = Event()


def punch_send(peer_ip: str, peer_port: int) -> object:
    hp_send_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    hp_send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    hp_send_sock.bind(('0.0.0.0', peer_port))
    hp_send_sock.settimeout(3)
    while not stop.is_set():
        try:
            hp_send_sock.connect((peer_ip, peer_port))
        except:
            print('restarting sender...')
            continue
        print('punch_send finished')
        stop.set()
        working_sock.append(hp_send_sock)


def punch_recv(sock: object, peer_ip: str, peer_port: int) -> object:
    print("started holepunch")
    punch_send_thr = Thread(
        target=punch_send, args=(peer_ip, peer_port), daemon=True)
    punch_send_thr.start()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.settimeout(5)
    sock.listen()
    while not stop.is_set():
        try:
            conn, addr = sock.accept()
        except socket.timeout:
            print('restarting listener...')
            continue
        print('punch_recv finished')
        stop.set()
        working_sock.append(conn)
    return working_sock[0]
