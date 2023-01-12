import enum
import json
import socket
import argparse
import threading
import typing as tp
from NEW.KVServer import KVServer

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
        person = {}
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

            if msg.lower().startswith('put'):
                try:
                    _, data = msg.split(' ', 1)
                    dict_data = json.loads(data)
                    for key, value in dict_data.items():
                        person[key] = value
                except json.JSONDecodeError:
                    conn.send('ERROR'.encode(self.format))

                conn.send('OK'.encode(self.format))

            elif msg.lower().startswith('get'):
                _, key = msg.split(' ')
                results = person.get(key)

                if results is None:
                    conn.send('Not found'.encode())

                conn.send(json.dumps(results).encode(self.format))

            elif msg.lower().startswith('delete'):
                print(data)

            elif msg.lower().startswith('query'):
                print(data)

            elif msg.lower().startswith('compute'):
                print(data)

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
            print("Close the server")


def run_server_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p",
        help="Socket port",
        type=int_type,
        required=True
    )
    parser.add_argument(
        "-a",
        help="Socket IP",
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


if __name__ == "__main__":
    main()
