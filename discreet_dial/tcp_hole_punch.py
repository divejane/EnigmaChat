import socket
import asyncio


async def punch_send(peer_ip: str, peer_port: int) -> object:
    hp_send_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:

        try:
            await hp_send_sock.connect((peer_ip, peer_port))
        except ConnectionRefusedError:
            continue
        return hp_send_sock


def punch_recv(sock: object, peer_ip: str, peer_port: int) -> object:
    punch_send_thr = punch_send(peer_ip, peer_port)
    while punch_send_thr is None:
        try:
            conn, addr = sock.accept()
        except socket.timeout:
            continue
        return conn
    return punch_send_thr


def h_punch(sock: object, peer_ip: str, peer_port: int):
    working_socket = asyncio.run(punch_recv(sock, peer_ip, peer_port))
