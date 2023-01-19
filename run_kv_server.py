import json
import socket
import argparse
import threading
import typing as tp
from KVServer import KVServer

class Server:
    def __init__(self, port: int, host: str) -> None:
        self.host = host
        self.port = port
        self.format = 'utf-8'
        self.head = 10000
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        self.threads: tp.List[threading.Thread] = []

    def handle_client(self, conn: socket.socket, addr: tp.Tuple[tp.Any, ...], running):
        print(f'[Server Thread]: New connection {addr} connected')
        connected = True
        kv_server = KVServer()
        while connected and running:
            msg = conn.recv(self.head).decode(self.format)

            if not msg:
                continue

            if msg.lower().startswith('exit'):
                connected = False
                conn.send('OK'.encode(self.format))
                continue

            if msg.lower().startswith('ping'):
                conn.send('PONG'.encode(self.format))

            if msg.lower().startswith('put'):
                _, data_str = msg.split(' ', 1)
                try:
                    # Load the data from the string
                    data_to_put = json.loads(data_str)
                    for key, value in data_to_put.items():
                        kv_server.put_request(key, value)
                    conn.send('OK'.encode(self.format))

                except json.JSONDecodeError:
                    conn.send('ERROR'.encode(self.format))

                except Exception as error:
                    # Server error
                    print("[Server Thread]:", error)
                    conn.send('ERROR'.encode(self.format))

            elif msg.lower().startswith('get'):
                print("[Server Thread]: GET", msg)
                try:
                    _, key = msg.split(' ', 1)
                    get_result = kv_server.get_request(key)

                    if get_result is None:
                        conn.send('NOT FOUND'.encode(self.format))
                        continue
                    
                    # TODO: Check if "get_request" returns `null` value
                    if get_result == "null":
                        conn.send(f'“{key}” -> []'.encode(self.format))
                        continue
                    
                    conn.send(f"“{key}” -> {print_data(get_result)}".encode(self.format))

                except (ValueError, TypeError) as error:
                    print("[Server Thread]: Server-Error:",  error)

            elif msg.lower().startswith('delete'):
                _, key = msg.split(' ')
                try:
                    kv_server.delete_request(key)
                    conn.send('OK'.encode(self.format))
                except:
                    conn.send('ERROR'.encode(self.format))

            elif msg.lower().startswith('query'):
                _, keypath = msg.split(' ')
                try:
                    query_result = kv_server.query_request(keypath)

                except Exception:
                    conn.send('NOT FOUND'.encode(self.format))
                    continue

                if query_result is None:
                    conn.send('NOT FOUND'.encode(self.format))
                    continue
                
                if isinstance(query_result, str):
                    conn.send(f'“{key}” -> {query_result}'.encode(self.format))
                    continue
                
                conn.send(f"“{key}” -> {print_data(get_result)}".encode(self.format))

            elif msg.lower().startswith('compute'):
                try:
                    compute_result = kv_server.compute_request(msg.upper())

                except Exception:
                    conn.send('NOT FOUND'.encode(self.format))
                    continue

                if compute_result is None:
                    conn.send('Not found'.encode())
                    continue

                # !ERROR: Check the results of compute
                conn.send(str(compute_result).encode(self.format))

        print("[Server Thread]: Client disconnect!")
        conn.close()

    def start(self):
        self.server_socket.listen()

        try:
            while True:
                conn, addr = self.server_socket.accept()
                running = threading.Event()
                running.set()
                thread = threading.Thread(
                    target=self.handle_client,
                    args=(conn, addr, running)
                )

                self.threads.append(thread)
                thread.start()

        except KeyboardInterrupt:
            print("[Server]: Stopped by Ctrl+C")

        finally:
            self.server_socket.close()
            for thread in self.threads:
                thread.join(timeout=2)

def print_data(obj: dict) -> str:

    def handle_value(v):
        if isinstance(v, dict):
            return f'[ {print_data(v)} ]'

        elif isinstance(v, list):
            return f'[ {" | ".join(f"{handle_value(element)}" for element in v)} ]'

        elif isinstance(v, (int, float)):
            return str(v)

        elif v is None:
            return 'null'

        return f'“{str(v)}”'

    return f' | '.join([F'“{k}” -> {handle_value(v)}' for k, v in obj.items()])


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


if __name__ == '__main__':
    main()
