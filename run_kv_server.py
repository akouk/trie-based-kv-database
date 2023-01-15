import enum
import json
import socket
import argparse
import threading
import typing as tp
from KVServer import KVServer

class Message(str, enum.Enum):
    ping = 'PING'
    exit = 'EXIT'


class Server(KVServer):
    def __init__(self, port: int, host: str) -> None:
        super().__init__(port, host)
        self.format = 'utf-8'
        self.head = 1024
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)

    def handle_client(self, conn: socket.socket, addr: tp.Tuple[tp.Any, ...]):
        print(f'New connection {addr} connected')
        connected = True

        while connected:
            msg = conn.recv(self.head).decode(self.format)

            if not msg:
                continue

            if msg == Message.exit:
                connected = False
                continue

            if msg == Message.ping:
                conn.send('PONG'.encode(self.format))

            
            if msg.lower().startswith('PUT'):
                _, data_str = msg.split(' ', 1)
                try:
                    data_to_put = json.loads(data_str) # Load the data from the string
                    for key, value in data_to_put.items():
                        Server.put_request(key, value)
                    conn.send('OK'.encode(self.format))
                except json.JSONDecodeError:
                    conn.send('ERROR'.encode(self.format))

                

            elif msg.lower().startswith('GET'):
                _, key = msg.split(' ')
                get_result = Server.get_request(key)

                if get_result is None:
                    conn.send('NOT FOUND'.encode())

                conn.send(json.dumps(get_result).encode(self.format))

            elif msg.lower().startswith('DELETE'):
                _, key = msg.split(' ')
                delete_request = Server.delete_request(key)

                if delete_request:
                    conn.send('OK'.encode(self.format))
                
                else:
                    conn.send('ERROR'.encode())
                

            elif msg.lower().startswith('QUERY'):
                _, keypath = msg.split(' ')
                query_result = Server.query_request(keypath)

                if query_result is None:
                    conn.send('NOT FOUND'.encode())
                
                conn.send(json.dumps(query_result).encode(self.format))

            elif msg.lower().startswith('COMPUTE'):
                compute_result = Server.compute_request(msg)

                if compute_result is None:
                    conn.send('Not found'.encode())
                
                conn.send(json.dumps(compute_result).encode(self.format))


    def start(self):
        self.server_socket.listen()
        try:
            while True:
                conn, addr = self.server_socket.accept()
                thread = threading.Thread(
                    target=self.handle_client, args=(conn, addr)
                )
                try:
                    thread.start()
                except KeyboardInterrupt:
                    thread.join()
                    break
        except KeyboardInterrupt:
            print('Close the server')


def run_server_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-p',
        help='Socket port',
        type=int_type,
        required=True
    )
    parser.add_argument(
        '-a',
        help='Socket IP',
        type=str,
        required=True
    )
    args = parser.parse_args()
    return args


def int_type(arg):
    if not arg.isdigit():
        raise argparse.ArgumentTypeError(
            f'Error: {arg} is not an integer. Please provide an integer as argument!')
    return int(arg)


def main():
    args = run_server_arguments()
    server = Server(args.p, args.a)
    server.start()
    server.port


if __name__ == '__main__':
    main()

    ## python3 run_server.py -p 5000 -a localhost
    ## python3 run_server.py -p 4000 -a localhost
    ## python3 run_server.py -p 7000 -a localhost
    ## python3 run_server.py -p 9000 -a localhost
