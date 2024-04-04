# TODO: remove all db lines, including the fake hostlist in the server
# TODO: comment this stuff i know its bad im sorry ill work on it im sorry please dont kill me

import os
import pickle
import socket
import threading

HOST = "3.15.139.172"
PORT = 9236

username = "anon" # default username

cls = lambda: os.system("cls" if os.name == "nt" else "clear") # screen clear lambda function

def drawLogo(): # prints 'dial' ascii to terminal 
    print('\x1b[1;31m' +
        "\n ██▄   ▄█ ██   █\n █  █  ██ █ █  █ \n █   █ ██ █▄▄█ █ \n █  █  ▐█ █  █ ███▄\n ███▀   ▐    █     ▀\n            █\n            █                  \n\n" + '\033[0m'
        
    )

# value within range check
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


# room loading
def roomlist_load():  # list room names
    # request list of rooms from server
    cls()
    roomrequest_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    roomrequest_s.connect((HOST, PORT))
    roomrequest_s.sendall(b"roomrequest")
    open_hosts = pickle.loads(roomrequest_s.recv(1024)) # unpickles hostlist sent by server from roomrequest

    # print room names w/ formatting
    print("|     room name     |\n") 
    for x, roomname in enumerate(open_hosts[1:]):
        print(f"{x+1}) {roomname[2]}")
    print("____________________")
    print("\nenter room to join (0 to exit) -")
    usinp = point_check(len(open_hosts) - 1)

    # exit if usinp == 0
    if usinp == 0:
        main()

    # send request to server to delete room information
    else:
        roomjoin_load(roomrequest_s, usinp, open_hosts) # starts loading screen


# room creation
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


# settings menu
def settings():
    cls()
    global username # spaghetti

    drawLogo()  
    print(f'1) change username ("{username}")\n2) back')
    usinp = point_check(2)
    if usinp == 1:
        username = input("enter username: ")
        settings()
    if usinp == 2:
        main()


# loading screens for client and host
def roomjoin_load(jgen_s, rqst_room, hlist):
    cls()
    jgen_s.sendall(f"rmrequest{rqst_room}".encode()) # sends goodbye message with room deletion request
    jgen_s.close()
    drawLogo()
    print("sent host connection info...")
    print(hlist[rqst_room][0], PORT) # prints peer ip and listening port
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
    # this looks somehwat jank to the naked eye, but the basic premise is that the program wipes the 'enter message:' input line, then
    # prints the recv message, then reprints the phrase 'enter message', without using input. This is because the console is still 
    # waiting for user input at a certain point in the terminal, so all we have to do is shift the terminal down by 1, which shifts the 
    # point waiting for user input. From there, we can print the recv message, then move the pointer back down to the point listening for 
    # user input.
    while True:
        inc_m = pt_conn.recv(1024)
        print('\u001B[2K', end='')    # erase line 
        print("\u001B[F", end='')     # move cursor up one line and move to beginning
        if (inc_m == b''): # if recv returns nothing in bytes, the connection has been closed
            print("\n\u001B[5mconnection ended, type '/exit' to leave\u001B[0m") # allows the user to review their message history before leaving
            print("\u001B[999D", end="")  # move cursor to beginning of line (might break)
            print('\nenter message: ', end='') 
            pt_conn.close()
            break
        print(f'\n{pt_addr}: {inc_m.decode()}')
        print("\u001B[999D", end="")  # move cursor to beginning of line
        print('\nenter message: ', end='')

def chatroom(pt_conn, pt_addr): 
    cls()
    drawLogo()
    print(f"connected to {pt_addr}, type '/exit' to leave")
    conn_read_thr = threading.Thread(target=conn_read, args=(pt_conn, pt_addr), daemon=True) # daemon because god knows this thing is going to crash
    conn_read_thr.start()
    # same concept as conn_read(), just shifting stuff around to be able to print above input then jumping back down to the the point waiting for input 
    while True: # This needs end conditions eventually, until then, kb_interupt to end chatting
        usinp = input("\nenter message: ")
        print("\u001B[A", end="")     # move cursor up one line
        print('\u001B[2K', end='')    # erase line 
        print(f'you: {usinp}') 
        print("\u001B[L", end="")     # insert new line
        print("\u001B[999C", end="")  # move cursor to beginning of line
        if (usinp == '/exit'): 
            try: 
                pt_conn.shutdown(socket.SHUT_RDWR) # when /exit is called, the socket is force closed and then deallocated. Shutdown is in a try: because the client will throw an error if it tries to shutdown a socket that's already been shutdown.
            except OSError:
                pass 
            pt_conn.close()
            main()
        try: 
            pt_conn.sendall(usinp.encode())        
        except:
            pass

# homepage
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
