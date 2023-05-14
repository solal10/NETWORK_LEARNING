import socket
import struct
import threading

ports = [5555, 5556, 5557, 5558, 5559]
servers_wth_port_socket, users, servers_wth_port_ip, users_frm_other_servers = dict(), dict(), dict(), dict()
choice = int(
    input("Please select the desired index between :\n \t0. 5555\n \t1. 5556\n \t2. 5557\n \t3. 5558\n \t4. 5559\n->"))
while choice < 0 or choice > 4:
    print("Error. Your choice is wrong")
    choice = int(input(
        "Please select the desired index between :\n \t0. 5555\n \t1. 5556\n \t2. 5557\n \t3. 5558\n \t4. 5559\n->"))
myport = ports[choice]

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('0.0.0.0', myport))
sock.listen(1)


def set_data(dict):
    strr = ""
    for i in dict:
        strr += str(dict[i]) + ':' + str(i) + "\0"
    return strr


def manage_data(str):
    lst = str[:-1].split("\0")
    tmp = dict()
    for k in lst:
        info = k.split(':')
        tmp[int(info[1])] = info[0]
    return tmp


def get_key_by_value(d, value):
    for k, v in d.items():
        if v == value:
            return k
    # Value not found
    return None


def respond_to_client(conn_socket, client_address):
    print(f"\tStart listening from {client_address}")
    while True:
        head = conn_socket.recv(6)
        if not head or len(head) < 6:
            break
        type, subtype, length, sublen = struct.unpack(">bbhh", head)

        if type == 0:
            if subtype == 0:
                data = set_data(servers_wth_port_ip)
                servers_wth_port_socket[client_address[1]] = conn_socket
                servers_wth_port_ip[client_address[1]] = '127.0.0.1'
            elif subtype == 1:
                data = '\0'.join(users.keys())
            conn_socket.send(struct.pack(">bbhh", 1, subtype, len(data), 0) + data.encode())
        elif type == 1:
            datarcv = conn_socket.recv(length).decode()
            if datarcv:
                if subtype == 0:
                    data = manage_data(datarcv)
                    degel = 1
                    for new_port in data.keys():
                        if new_port != myport and new_port not in servers_wth_port_ip:
                            try:
                                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
                                client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                                client.bind(('127.0.0.1', myport))
                                client.connect(('127.0.0.1', new_port))
                                client.send(struct.pack(">bbhh", 0, 0, 0, 0))
                                servers_wth_port_socket[new_port] = client
                                servers_wth_port_ip[new_port] = '127.0.0.1'
                                client.send(struct.pack(">bbhh", 0, 1, 0, 0))
                                degel = 0
                            except ConnectionRefusedError:
                                print("ConnectionRefusedError")
                        if degel == 0:
                            threading.Thread(target=respond_to_client,
                                             args=(servers_wth_port_socket[new_port], ('127.0.0.1', new_port))).start()

                elif subtype == 1:
                    data = {key: client_address for key in datarcv.split('\0')}
                    for new_clients in data.keys():
                        if new_clients not in users and new_clients not in users_frm_other_servers:
                            users_frm_other_servers[new_clients] = data[new_clients]
        elif type == 2:
            if subtype == 1:
                data = conn_socket.recv(length).decode()
                users[data] = conn_socket
                print(f'\t\tConnected to {client_address}')
        elif type == 3:
            receiver = conn_socket.recv(sublen).decode()
            message = conn_socket.recv(length).decode()
            if len(receiver.split('\0')[0]) == len(receiver):
                if receiver.strip() in users.keys():
                    data = get_key_by_value(users, conn_socket) + '\0' + receiver + message
                    try:
                        users[receiver.strip()].send(struct.pack(">bbhh", type, 0, len(data), len(data) - len(message)) + data.encode())
                        print('Message received from {0}\n\t Transfered to {1}'.format(client_address, users[receiver.strip()].getpeername()))
                    except Exception as e:
                        print(f"Error sending message to {users[receiver].getpeername()}: {e}")
                else:
                    # Receiver user not found in connected_users
                    # Send message to all servers in the network
                    data = str(client_address) + '\0' + receiver + message
                    for server_sock in servers_wth_port_socket.values():
                        try:
                          server_sock.send(struct.pack(">bbhh", type, 0, len(data), len(data) - len(message)) + data.encode())
                        except Exception as e:
                            print(f"Error sending message to {server_sock.getpeername()}: {e}")
                    print('Message received from {0}\n\t Transfered to all the connected servers'.format(client_address))
            else:
                # message was transferred from another server
                sender, receiver = receiver.split('\0')
                data = sender + '\0' + receiver + message
                if receiver.strip() in users.keys():
                    # message is intended for a connected user on this server
                    try:
                        users[receiver.strip()].send(struct.pack(">bbhh", type, 0, len(data), len(data) - len(message)) + data.encode())
                        print('Message received from {0}\n\t Transfered to {1}'.format(client_address, users[receiver.strip()].getpeername()))
                    except Exception as e:
                        print(f"Error sending message to {users[receiver.strip()].getpeername()}: {e}")
                else:
                    print('Message received from {0}\n\t'.format(client_address))


def waiting_to_other_ports():
    while True:
        conn, client_address = sock.accept()
        print('New connection from', client_address)
        threading.Thread(target=respond_to_client, args=(conn, client_address)).start()


threading.Thread(target=waiting_to_other_ports, args=()).start()
degel = 1
for i in range(5):
    if ports[i] != myport and ports[i] not in servers_wth_port_socket:
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
            client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            client.bind(('127.0.0.1', myport))
            client.connect(('127.0.0.1', ports[i]))
            client.send(struct.pack(">bbhh", 0, 0, 0, 0))
            servers_wth_port_socket[ports[i]] = client
            servers_wth_port_ip[ports[i]] = '127.0.0.1'
            client.send(struct.pack(">bbhh", 0, 1, 0, 0))
            print(f"Connected to port {client.getpeername()}")
            goodport = ports[i]
            degel = 0
            break
        except ConnectionRefusedError:
            print("ConnectionRefusedError")
if degel == 0:
    threading.Thread(target=respond_to_client, args=(servers_wth_port_socket[goodport], ('127.0.0.1', goodport))).start()