# TODO: remove all db lines, including the fake hostlist in the server
# TODO: fix incoming messages not being displayed correctly **
# TODO: comment this stuff i know its bad im sorry ill work on it im sorry please dont kill me

import os
import pickle
import socket
import threading

HOST = "3.15.139.172"
PORT = 9236

username = "anon"

cls = lambda: os.system("cls" if os.name == "nt" else "clear")

def drawLogo():
    print('\x1b[1;31m' +
        "\n ██▄   ▄█ ██   █\n █  █  ██ █ █  █ \n █   █ ██ █▄▄█ █ \n █  █  ▐█ █  █ ███▄\n ███▀   ▐    █     ▀\n            █\n            █                  \n\n" + '\033[0m'
        
    )

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
    drawLogo()
    while True:
        roomname = input("enter room name: ")
        password = input("enter room password: ")
        if 0 < len(roomname) < 16 and 0 < len(password) < 16:
            host_info = pickle.dumps([roomname, password])
            hostgen_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print('\nattempting to connect to server...')
            hostgen_s.connect((HOST, PORT))
            hostgen_s.sendall(host_info)
            hostgen_s.close()
            break

        print("room name and/or password must be between 0 and 16 characters\n")
    # print(f"\nverify room information: \nroom name: {roomname}\nroom password: {password}") # +wait
    print("room configured")
    roomhost_load()


# Settings menu
def settings():
    cls()
    global username

    drawLogo()  
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
    drawLogo()
    print("sent host connection info...")
    print(hlist[rqst_room][0], PORT)
    js = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    js.connect(("127.0.0.1", PORT)) # need 127.0.0.1 to be a variable
    print("\nconnection successful, please wait...")
    chatroom(js, "127.0.0.1")


def roomhost_load():
    cls()
    drawLogo()
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
        print('\u001B[2K', end='')    # Erase line 
        print("\u001B7", end="")      # Save current cursor position
        print("\u001B[A", end="")     # Move cursor up one line
        print("\u001B[999D", end="")  # Move cursor to beginning of line
        print("\u001B[S", end="")     # Scroll up/pan window down 1 line
        print("\u001B[L", end="")     # Insert new line
        if (inc_m == b''): 
            print("connection ended, type '/exit' to leave")
            print('enter message: ')
            # print('\u001B8', end='')
            pt_conn.close()
            break
        print(f'\n{pt_addr}: {inc_m.decode()}')
        print('enter message: ')
        print('\u001B8', end='')

def chatroom(pt_conn, pt_addr): 
    cls()
    drawLogo()
    print(f'connected to {pt_addr}')
    conn_read_thr = threading.Thread(target=conn_read, args=(pt_conn, pt_addr), daemon=True)
    conn_read_thr.start()
    while True: # This needs end conditions eventually, until then, kb_interupt to end chatting
        print("\u001B7", end="")      # Save current cursor position
        usinp = input("enter messsage: ")
        #print(f'you: {usinp}')
        if (usinp == '/exit'): 
            main()
        pt_conn.sendall(usinp.encode())
        print('\u001B8', end='')


# Homepage
def main():
    cls()
    
    drawLogo()
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
