from threading import Thread
import socket
import sys
import struct

ports = [5555, 5556, 5557, 5558, 5559]

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


x = Thread(target=output_recvfrom, args=(sock, ))
x.start()
print("Enter the receiver name + your message from now: ")
for line in sys.stdin:
    data = line.strip()
    sock.send(struct.pack('>bbhh', 3, 0, len(data), len(data.split(" ", 1)[0]) + 1) + data.encode())
x.join()



