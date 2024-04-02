# TODO: remove all db lines, including the fake hostlist in the server
# TODO: fix the daemon thread not being ended, which bugs out the address and keeps it in use
# TODO: fix incoming messages not being displayed correctly

import os
import pickle
import socket
import threading

HOST = "3.15.139.172"
PORT = 9236

username = "anon"

cls = lambda: os.system("cls" if os.name == "nt" else "clear")


# Value within range check
def point_check(max):  # return user input if within a range
    while True:
        try:
            usinp = int(input("$: "))
        except KeyboardInterrupt:
            quit()  # ^C break
        except:
            continue
        if 0 <= usinp <= max:
            return usinp


# Room loading
def roomlist_load():  # List room names
    # Request list of rooms from server
    cls()
    roomrequest_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    roomrequest_s.connect((HOST, PORT))
    roomrequest_s.sendall(b"roomrequest")
    open_hosts = pickle.loads(roomrequest_s.recv(1024))

    # Print room names w/ formatting
    print("|     room name     |\n")
    for x, roomname in enumerate(open_hosts[1:]):
        print(f"{x+1}) {roomname[2]}")
    print("____________________")
    print("\nenter room to join (0 to exit) -")
    usinp = point_check(len(open_hosts) - 1)

    # Exit if usinp == 0
    if usinp == 0:
        main()

    # Send request to server to delete room information
    else:
        roomjoin_load(roomrequest_s, usinp, open_hosts)


# Room creation
def room_gen():
    cls()
    print(
        "           _                \n ___ ___  (_)__ ___ _  ___ _\n/ -_) _ \/ / _ `/  ' \/ _ `/\n\__/_//_/_/\_, /_/_/_/\_,_/ \n          /___/             \n\n"
    )
    while True:
        roomname = input("enter room name: ")
        password = input("enter room password: ")
        if 0 < len(roomname) < 16 and 0 < len(password) < 16:
            host_info = pickle.dumps([roomname, password])
            hostgen_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            hostgen_s.connect((HOST, PORT))
            hostgen_s.sendall(host_info)
            hostgen_s.close()
            break

        print("room name and/or password must not be longer than 16 characters\n")
    # print(f"\nverify room information: \nroom name: {roomname}\nroom password: {password}") # +wait
    print("room configured")
    roomhost_load()


# Settings menu
def settings():
    cls()
    global username

    print(
        "           _                \n ___ ___  (_)__ ___ _  ___ _\n/ -_) _ \/ / _ `/  ' \/ _ `/\n\__/_//_/_/\_, /_/_/_/\_,_/ \n          /___/             \n\n"
    )
    print(f'1) change username ("{username}")\n2) back')
    usinp = point_check(2)
    if usinp == 1:
        username = input("enter username: ")
        settings()
    if usinp == 2:
        main()


# Loading screens for client and host
def roomjoin_load(jgen_s, rqst_room, hlist):
    cls()
    jgen_s.sendall(f"rmrequest{rqst_room}".encode())
    jgen_s.close()
    print(
        "           _                \n ___ ___  (_)__ ___ _  ___ _\n/ -_) _ \/ / _ `/  ' \/ _ `/\n\__/_//_/_/\_, /_/_/_/\_,_/ \n          /___/             \n\n"
    )
    print("sent host connection info...")
    print(hlist[rqst_room][0], PORT)
    js = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    js.connect(("127.0.0.1", PORT)) # need 127.0.0.1 to be a variable
    print("\nconnection successful, please wait...")
    chatroom(js, "127.0.0.1")


def roomhost_load():
    cls()
    print(
        "           _                \n ___ ___  (_)__ ___ _  ___ _\n/ -_) _ \/ / _ `/  ' \/ _ `/\n\__/_//_/_/\_, /_/_/_/\_,_/ \n          /___/             \n\n"
    )
    print("\n\nroom configured, awaiting peer establishment...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", PORT))
    s.listen()
    conn, addr = s.accept()
    print("\nconnection successful, please wait...")
    chatroom(conn, addr[0])

def conn_read(pt_conn, pt_addr):
    while True:
        inc_m = pt_conn.recv(1024)
        if (inc_m == 0): continue
        print("\u001B[s", end="")     # Save current cursor position
        print("\u001B[A", end="")     # Move cursor up one line
        print("\u001B[L", end="")     # Insert new line
        print(f'\n{pt_addr}: {inc_m.decode()}')
        print("\u001B[u", end="")     # Jump back to saved cursor position

def chatroom(pt_conn, pt_addr):
    cls()
    print(
        "           _                \n ___ ___  (_)__ ___ _  ___ _\n/ -_) _ \/ / _ `/  ' \/ _ `/\n\__/_//_/_/\_, /_/_/_/\_,_/ \n          /___/             \n\n"
    )
    print(f'connected to {pt_addr}')
    conn_read_thr = threading.Thread(target=conn_read, args=(pt_conn, pt_addr), daemon=True)
    conn_read_thr.start()
    while True: # This needs end conditions eventually, until then, kb_interupt to end chatting
        usinp = input("enter messsage: ")
        pt_conn.sendall(usinp.encode())


# Homepage
def main():
    cls()

    print(
        "           _                \n ___ ___  (_)__ ___ _  ___ _\n/ -_) _ \/ / _ `/  ' \/ _ `/\n\__/_//_/_/\_, /_/_/_/\_,_/ \n          /___/             \n\n"
    )
    print("1) join a room\n2) create a room\n3) settings\n")

    point = point_check(3)

    if point == 1:
        roomlist_load()
    if point == 2:
        room_gen()
    if point == 3:
        settings()


if __name__ == "__main__":
    main()
