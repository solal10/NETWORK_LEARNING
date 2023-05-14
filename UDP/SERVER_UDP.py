import socket
UDP_IP = '0.0.0.0'
UDP_PORT = 9999
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
sock.bind((UDP_IP, UDP_PORT))

clients = {}
while True:
    data, addr = sock.recvfrom(1024)
    if addr in clients.values():
        info = data.decode().split(" ", 1)
        if len(info) == 1:
            sock.sendto("Error try again. Please check your input".encode(), addr)
        else:
            name = info[0]
            if name in clients:
                print('Message received from {0} for {1}: {2}'.format(addr, clients[info[0]], info[1]))
                sock.sendto(("New message: " + info[1]).encode(), clients[name])
                sock.sendto('Your message has been received'.encode(), addr)
                print("\t Has been sent")
            else:
                print("Message received from {0} for {1}: {2}\n\t-> Hasn't been sent : no user with this name".format(addr, info[0], info[1]))
                sock.sendto("There is no user with this name".encode(), addr)
    elif len(data.decode().split()) == 1:
        print('New user : ', data.decode())
        clients[data.decode()] = addr
    else:
        sock.sendto("Error try again. Please enter just your first name".encode(), addr)
