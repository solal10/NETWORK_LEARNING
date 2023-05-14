import socket
import threading

ports = [5555, 5556, 5557, 5558, 5559]
choice = int(input("Please select the desired index between :\n \t0. 5555\n \t1. 5556\n \t2. 5557\n \t3. 5558\n \t4. 5559\n->"))
while choice < 0 or choice > 4:
    print("Error. Your choice is wrong")
    choice = int(input("Please select the desired index between :\n \t0. 5555\n \t1. 5556\n \t2. 5557\n \t3. 5558\n \t4. 5559\n->"))
port = ports[choice]

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
sock.bind(('0.0.0.0', ports[choice]))
sock.listen(1)


def respond_to_client(conn_socket, client_address):
    print(f"\tStart listening from {client_address}")
    while True:
        data = conn_socket.recv(1024)
        if not data:
            break
        print(f'\t\tData received from {client_address} : {data.decode()}')
        conn_socket.send(b'World')


def waiting_to_other_ports():
    while True:
        conn, client_address = sock.accept()
        print('New connection from', client_address)
        threading.Thread(target=respond_to_client, args=(conn, client_address)).start()


threading.Thread(target=waiting_to_other_ports, args=()).start()
for other_port in ports:
    if other_port != port:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
            client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            client.bind(('127.0.0.1', port))
            client.connect(('127.0.0.1', other_port))

            client.send(b"Hello")
            data = client.recv(1024)
            if data.decode() == "World":
                print(f'Data received : {data.decode()}')
                print(f"\tConnected to port {other_port}")
            client.close()
        except ConnectionRefusedError:
            print("ConnectionRefusedError")
