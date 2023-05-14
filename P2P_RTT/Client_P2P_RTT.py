import threading
import time
from threading import Thread
import socket
import sys
import struct


def manage_data(str):
    lst = str[:-1].split("\0")
    tmp = dict()
    for k in lst:
        info = k.split(':')
        tmp[int(info[1])] = info[0]
    return tmp


def handling_running_server(port_connection):
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        client.bind(('127.0.0.1', 9999))
        client.connect(port_connection)
        start = time.time()
        client.send(struct.pack(">bbhh", 4, 0, 0, 0))
        client.recv(6)
        done = time.time()
        elapsed = done - start
        running_server_rtt[client] = elapsed

    except ConnectionRefusedError:
        print("ConnectionRefusedError")


ports = [5555, 5556, 5557, 5558, 5559]
running_server_rtt={}
choice = int(
    input("Please select the desired index between :\n \t0. 5555\n \t1. 5556\n \t2. 5557\n \t3. 5558\n \t4. 5559\n->"))
while choice < 0 or choice > 4:
    print("Error. Your choice is wrong")
    choice = int(input(
        "Please select the desired index between :\n \t0. 5555\n \t1. 5556\n \t2. 5557\n \t3. 5558\n \t4. 5559\n->"))
port = ports[choice]

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

sock.bind(('127.0.0.1', 9999))
sock.connect(('127.0.0.1', port))
type, subtype, lenght, sublen = 0, 0, 0, 0
sock.send(struct.pack('>bbhh', type, subtype, lenght, sublen))
head = sock.recv(6)
type, subtype, length, sublen = struct.unpack(">bbhh", head)
datarcv = sock.recv(length).decode()
start = time.time()
sock.send(struct.pack(">bbhh", 4, 0, 0, 0))
sock.recv(6)
done=time.time()
elapsed=done-start
running_server_rtt[sock]=elapsed

if datarcv:
    data = manage_data(datarcv)
    data[port] = '127.0.0.1'
    threads = []
    for new_port in data.keys():
        if new_port != port and new_port not in running_server_rtt:
            t = threading.Thread(target=handling_running_server, args=(('127.0.0.1',new_port),))
            t.start()
            threads.append(t)
    for t in threads:
        t.join()
else:
    exit()
min_rtt_socket=min(running_server_rtt,key=running_server_rtt.get)
for socket in running_server_rtt:
    if socket != min_rtt_socket:
        socket.close()
sock=min_rtt_socket
name = input('Enter your name: ')
type, subtype, length, sublen = 2, 1, len(name), 0
sock.send(struct.pack('>bbhh', type, subtype, length, sublen) + name.encode())


def output_recvfrom(sock):
    while True:
        head = sock.recv(6)
        if not head or len(head) < 6:
            break
        type, subtype, length, sublen = struct.unpack(">bbhh", head)
        fromto = sock.recv(sublen).decode()
        sender, receiver = fromto.strip().split("\0")
        message = sock.recv(length).decode()
        print('\t\tMessage received from {0} : {1}'.format(sender, message))


x = Thread(target=output_recvfrom, args=(sock,))
x.start()
print("Enter the receiver name + your message from now: ")
for line in sys.stdin:
    data = line.strip()
    sock.send(struct.pack('>bbhh', 3, 0, len(data), len(data.split(" ", 1)[0]) + 1) + data.encode())
x.join()


