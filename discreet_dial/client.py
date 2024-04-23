# TODO: p2p encrypt & nat hole punch: these are the last things to do before 1.0 release
# TODO: the serverside code for socketio is for the most part done, still need to do socketio client. Also need to actually do the threading/async
# for the hole punch. Try to make it only return one socket when the whole operation is over.

from requests import get, post, delete, exceptions
from threading import Thread
import socketio  # polling
import socket  # standard socket
import util
import tcp_hole_punch

HOST = "https://discreetdial.ddns.net/"


def cli_menu() -> None:
    """main menu screen where the user can select different paths"""
    conf = [
        "anon"]  # This will eventually be put into a dynamically generated 'config' file
    while True:
        util.cli_cls()
        util.cli_draw_logo()

        print("1) join a room\n2) create a room\n3) settings\n")

        point = util.valid_usinp(3)

        if point == 1:
            room_list_load(conf)
        elif point == 2:
            generate_room(conf)
        elif point == 3:
            conf = cli_settings(conf)


def generate_room(conf) -> None:
    """user generates room, room info is json'ed, sent off to server"""
    util.cli_cls()
    util.cli_draw_logo()

    while True:
        roomname = input("enter room name: ")
        password = input("enter room password: ")
        if 0 < len(roomname) < 16 and 0 < len(password) < 16:
            host_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            host_sock.bind(("0.0.0.0", 0))
            host_info = {'room_name': roomname,
                         'password': password,
                         'username': conf[0],
                         'is_password_protected': len(password) > 0,
                         'host_port': host_sock.getsockname()[1]}

            waitlist_sock = socketio.SimpleClient()
            waitlist_sock.connect(HOST)
            room_id = waitlist_sock.emit('addroom', host_info)
            print('\nattempting to connect to server...')
            break
        print("room name and/or password must be between 0 and 16 characters\n")
    print("room configured")
    room_host_load(host_sock, room_id, waitlist_sock)


def room_list_load(conf: list) -> None:
    """requests rooms from server, formats them, checks if selected rooms has a password, then sends the room_id + password to server to be
    checked"""
    util.cli_cls()
    util.cli_draw_logo()

    open_rooms = get(HOST + 'rooms')

    if open_rooms.text == 'no open rooms':
        print('no available rooms (0 to exit)\n')
        usinp = util.valid_usinp(0)
        if usinp == 0:
            return

    index_to_roomid = []

    print("\n~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~\n")
    print(
        "\x1b[1;31mi | room name        : username         |  password? (X)  |\033[0m\n")
    open_rooms = open_rooms.json()
    for x, room_info in enumerate(open_rooms.items()):
        index_to_roomid.append(room_info[0])
        print(
            f"{x+1} | {room_info[1]['room_name']:<16} {':'} {room_info[1]['username']:<24} {'(X)' if room_info[1]['is_password_protected'] else ''}")
    print("\n~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~")
    print("\nenter room to join (0 to exit) -")

    usinp = util.valid_usinp(len(open_rooms))

    if usinp == 0:
        return

    params = {
        'room_id': index_to_roomid[usinp-1],
        'password': ''
    }

    roomid_to_room = open_rooms[index_to_roomid[usinp-1]]
    if roomid_to_room['is_password_protected']:
        params['password'] = input('enter password: ')

    room_connect = get(HOST + 'firetrial', params=params)
    try:
        room_connect.raise_for_status()
    except exceptions.HTTPError:
        print('password was rejected (0 to exit)')
        if util.valid_usinp(0) == 0:
            return
    join_room_load(room_connect.json(), conf, roomid_to_room['username'])


def join_room_load(room_connect: dict, conf: list, peer_username: str) -> None:
    """attempts to connect to localhost on port, and connects to public ip if that fails. sends username on socket init"""
    util.cli_cls()
    util.cli_draw_logo()

    print("sent host connection info...")
    lh_attempt_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        lh_attempt_sock.connect(("0.0.0.0", int(room_connect['host_port'])))
    except ConnectionRefusedError:
        lh_attempt_sock.close()
        peer_join_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer_join_sock.bind(("0.0.0.0", room_connect['host_port']+1))
        peer_join_sock = tcp_hole_punch.punch_recv(
            peer_join_sock, room_connect['host_ip'], room_connect['host_port'])
    peer_join_sock.sendall(conf[0].encode())
    print("\nconnection successful, please wait...")
    chatroom(peer_join_sock, peer_username)


def room_host_load(host_sock: object, room_id: str, waitlist_sock: object) -> None:
    """listens until client connects, then sends off a room_id to the server so that the room can be deleted"""
    util.cli_cls()
    util.cli_draw_logo()

    print("\n\nroom configured, awaiting peer establishment...")
    peer_ip = waitlist_sock.receive()
    print("received peer info, connecting...")
    conn = tcp_hole_punch.punch_recv(
        host_sock, peer_ip[1], host_sock.getsockname()[1]+1)
    confirm_connect = delete(HOST + 'rooms', data={'room_id': room_id})
    print("\npeer connection successful, awaiting further info...")
    peer_username = conn.recv(1024).decode()
    print("peer connection success! please wait...")
    chatroom(conn, peer_username)


def conn_read(peer_connection: object, peer_username: str) -> None:
    """handles and prints new incoming messages"""
    # transforms interface if client recieves a message. Client clears 'enter message'input line, prints incoming message, then prints new 'enter message' text one line below
    while True:
        inc_m = peer_connection.recv(1024)
        if (inc_m == b''):  # if recv returns nothing in bytes, the connection has been closed
            # allows the user to review their message history before leaving
            print('\r{}\n\nenter message: '.format(
                "\u001B[5mconnection ended, type '/exit' to leave\u001B[0m"), end='')
            peer_connection.close()
            break
        print('\r\033[K' + peer_username +
              ': {}\n\nenter message: '.format((inc_m).decode()), end='')


def chatroom(peer_connection: object, peer_username: str) -> None:
    """handles outgoing messages and closing the room socket on disconnect"""
    util.cli_cls()
    util.cli_draw_logo()

    print(f"connected to {peer_username}, type '/exit' to leave")
    # daemon because god knows this thing is going to crash
    conn_read_thr = Thread(
        target=conn_read, args=(peer_connection, peer_username), daemon=True)
    conn_read_thr.start()
    # same concept as conn_read(), just shifting stuff around to be able to print above input then jumping back down to the the point waiting for input
    while True:
        usinp = input("\nenter message: ")
        if (usinp == '/exit'):
            try:
                # when /exit is called, the socket is force closed and then deallocated. Shutdown is in a try: because the client will throw an error if it tries to shutdown a socket that's already been shutdown.
                peer_connection.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            peer_connection.close()
            return
        try:  # in a try becase message sending will throw and error if the socket is closed, but we still want messages. bad and i will fix later
            peer_connection.sendall(usinp.encode())
        except:
            pass


def cli_settings(conf: list) -> list:
    """user configuration of conf"""
    while True:
        util.cli_cls()
        util.cli_draw_logo()

        print(f'1) change username ("{conf[0]}")\n2) back')
        usinp = util.valid_usinp(2)
        if usinp == 1:
            conf[0] = util.change_username()
        elif usinp == 2:
            break
    return conf
