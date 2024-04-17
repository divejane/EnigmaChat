# TODO: p2p encrypt & nat hole punch: these are the last things to do before 1.0 release

from requests import get, post, delete, exceptions
from os import name, system
from threading import Thread
import socket

HOST = "https://discreetdial.ddns.net/"


def change_username() -> None:
    return input("enter username: ")


def valid_usinp(max: int) -> int:
    """checks user input is valid type and within specified (max) range"""
    while True:
        try:
            usinp = int(input("$: "))
        except ValueError:
            continue
        if 0 <= usinp <= max:
            return usinp


def cli_cls() -> None:
    """clear console"""
    system("cls" if name == "nt" else "clear")


def cli_draw_logo() -> None:
    """draw 'discreet dial' logo to console"""
    print("\x1b[1;31m\n      ___                     __       ___      __\n  ___/ (_)__ ___________ ___ / /_  ___/ (_)__ _/ /\n / _  / (_-</ __/ __/ -_) -_) __/ / _  / / _ `/ /\n \_,_/_/___/\__/_/  \__/\__/\__/  \_,_/_/\_,_/_/\n\n \033[0m")


def cli_menu() -> None:
    """main menu screen where the user can select different paths"""
    conf = [
        "anon"]  # This will eventually be put into a dynamically generated 'config' file
    while True:
        cli_cls()
        cli_draw_logo()

        print("1) join a room\n2) create a room\n3) settings\n")

        point = valid_usinp(3)

        if point == 1:
            room_list_load(conf)
        elif point == 2:
            generate_room(conf)
        elif point == 3:
            conf = cli_settings(conf)


def generate_room(conf) -> None:
    """user generates room, room info is json'ed, sent off to server"""
    cli_cls()
    cli_draw_logo()

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

            room_id = (post(HOST + 'rooms', data=host_info))
            print('\nattempting to connect to server...')
            break
        print("room name and/or password must be between 0 and 16 characters\n")
    print("room configured")
    room_host_load(host_sock, room_id)


def room_list_load(conf: list) -> None:
    """requests rooms from server, formats them, checks if selected rooms has a password, then sends the room_id + password to server to be 
    checked"""
    cli_cls()
    cli_draw_logo()

    open_rooms = get(HOST + 'rooms')

    if open_rooms.text == 'nohosts':
        print('no available rooms (0 to exit)\n')
        usinp = valid_usinp(0)
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

    usinp = valid_usinp(len(open_rooms))

    if usinp == 0:
        return

    params = {
        'room_id': index_to_roomid[usinp-1],
        'password': ''
    }

    roomid_to_room = open_rooms[index_to_roomid[usinp-1]]
    if roomid_to_room['is_password_protected']:
        params['password'] = input('enter password: ')

    room_connect = get(HOST + 'firetrial', params=params).json()
    try:
        room_connect.raise_for_status()
    except exceptions.HTTPError:
        print('password was rejected (0 to exit)')
        if valid_usinp(0) == 0:
            return
    except AttributeError:
        join_room_load(room_connect, conf, roomid_to_room['username'])


def join_room_load(room_connect: dict, conf: list, peer_username: str) -> None:
    """attempts to connect to localhost on port, and connects to public ip if that fails. sends username on socket init"""
    cli_cls()
    cli_draw_logo()

    print("sent host connection info...")
    peer_join_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        peer_join_sock.connect(("0.0.0.0", int(room_connect['host_port'])))
    except ConnectionRefusedError:
        peer_join_sock.connect(
            (room_connect['host_ip'], int(room_connect['host_port'])))
    peer_join_sock.sendall(conf[0].encode())
    print("\nconnection successful, please wait...")
    chatroom(peer_join_sock, peer_username)


def room_host_load(host_sock: object, room_id: str) -> None:
    """listens until client connects, then sends off a room_id to the server so that the room can be deleted"""
    cli_cls()
    cli_draw_logo()

    print("\n\nroom configured, awaiting peer establishment...")
    host_sock.listen()
    conn, addr = host_sock.accept()
    confirm_connect = delete(HOST + 'rooms', data={'room_id': room_id})
    print("\npeer connection successful, awaiting further info...")
    peer_username = conn.recv(1024).decode()
    print("peer connection success! please wait...")
    chatroom(conn, peer_username)


def conn_read(peer_connection: object, peer_username: str) -> None:
    """handles new incoming messages, the codes that keep appearing in the print statements are known as 'ANSI' escape codes, used for 
    terminal control"""
    # transforms interface if client recieves a message. Client clears 'enter message'input line, prints incoming message, then prints new 'enter message' text one line below
    while True:
        inc_m = peer_connection.recv(1024)
        print('\u001B[2K', end='')    # erase line
        # move cursor up one line and move to beginning
        print("\u001B[F", end='')
        if (inc_m == b''):  # if recv returns nothing in bytes, the connection has been closed
            # allows the user to review their message history before leaving
            print(
                "\n\u001B[5mconnection ended, type '/exit' to leave\u001B[0m")
            # move cursor to beginning of line (might break)
            print("\u001B[999D", end="")
            print('\nenter message: ', end='')
            peer_connection.close()
            break
        print(f'\n{peer_username}: {inc_m.decode()}')
        print("\u001B[999D", end="")  # move cursor to beginning of line
        print('\nenter message: ', end='')


def chatroom(peer_connection: object, peer_username: str) -> None:
    """handles outgoing messages and closing the room socket on disconnect"""
    cli_cls()
    cli_draw_logo()

    print(f"connected to {peer_username}, type '/exit' to leave")
    # daemon because god knows this thing is going to crash
    conn_read_thr = Thread(
        target=conn_read, args=(peer_connection, peer_username), daemon=True)
    conn_read_thr.start()
    # same concept as conn_read(), just shifting stuff around to be able to print above input then jumping back down to the the point waiting for input
    while True:
        usinp = input("\nenter message: ")
        print("\u001B[A", end="")     # move cursor up one line
        print('\u001B[2K', end='')    # erase line
        print(f'you: {usinp}')
        print("\u001B[L", end="")     # insert new line
        print("\u001B[999C", end="")  # move cursor to beginning of line
        if (usinp == '/exit'):
            try:
                # when /exit is called, the socket is force closed and then deallocated. Shutdown is in a try: because the client will throw an error if it tries to shutdown a socket that's already been shutdown.
                peer_connection.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            peer_connection.close()
            return
        try:
            peer_connection.sendall(usinp.encode())
        except:
            pass


def cli_settings(conf: list) -> list:
    """user configuration of conf"""
    while True:
        cli_cls()
        cli_draw_logo()

        print(f'1) change username ("{conf[0]}")\n2) back')
        usinp = valid_usinp(2)
        if usinp == 1:
            conf[0] = change_username()
        elif usinp == 2:
            break
    return conf
