import json
import socket
import argparse
import threading
import typing as tp
from KVServer import KVServer

class Server:
    def __init__(self, port: int, host: str) -> None:
        """
        Constructor method for the Server class
        param
        Initialize the server with a given host and port
        """

        self.host = host
        self.port = port
        # Set the format for encoding and decoding messages to 'utf-8'
        self.format = 'utf-8'
        # Set the maximum size of messages to 10000 bytes
        self.head = 10000
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Bind the socket to the given host and port
        self.server_socket.bind((self.host, self.port))
        # Listen for client connections
        self.server_socket.listen(1)
        # Initialize an empty list to store client threads
        self.threads: tp.List[threading.Thread] = []

    def handle_client(self, conn: socket.socket, addr: tp.Tuple[tp.Any, ...], running):
        """
        Handle a client connection by processing messages and performing appropriate actions
        """

        # Print a message indicating that a new connection has been established
        print(f'[Server Thread]: New connection {addr} connected')
        # Set a variable to indicate that the client is connected
        connected = True
        kv_server = KVServer()
        # Enter a loop that continues as long as the client is connected and the server is running
        while connected and running:
            # Receive a message from the client
            msg = conn.recv(self.head).decode(self.format)
            
            if not msg:
                continue

            if msg.lower().startswith('exit'):
                connected = False
                conn.send('OK'.encode(self.format))
                continue
            
            # if the message starts with 'ping', send back a 'PONG' message
            if msg.lower().startswith('ping'):
                conn.send('PONG'.encode(self.format))

            if msg.lower().startswith('put'):
                _, data_str = msg.split(' ', 1)
                
                try:
                    data_to_put = json.loads(data_str)

                    for key, value in data_to_put.items():
                        kv_server.put_request(key, value)
                    conn.send('OK'.encode(self.format))

                except json.JSONDecodeError:
                    conn.send('ERROR'.encode(self.format))

                except Exception as error:
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
                    
                    conn.send(f"“{key}” -> {get_result}".encode(self.format))

                except (ValueError, TypeError) as error:
                    print("[Server Thread]: Server-Error:",  error)

            elif msg.lower().startswith('delete'):
                _, key = msg.split(' ')

                try:
                    kv_server.delete_request(key)

                except:
                    conn.send('ERROR'.encode(self.format))

                conn.send('OK'.encode(self.format))

            elif msg.lower().startswith('query'):
                _, keypath = msg.split(' ')
                
                try:
                    query_result = kv_server.query_request(keypath)

                except Exception:
                    conn.send('EXCEPTION ERROR'.encode(self.format))
                    continue

                if query_result is None:
                    conn.send('NOT FOUND'.encode(self.format))
                    continue
                
                if isinstance(query_result, str):
                    conn.send(f'“{keypath}” -> {query_result}'.encode(self.format))
                    continue
                
                conn.send(f"“{keypath}” -> {query_result}".encode(self.format))

            elif msg.lower().startswith('compute'):
                
                try:
                    computed_result = kv_server.compute_request(msg)
                    

                except Exception:
                    conn.send(('EXCEPTION ERROR!').encode(self.format))
                    continue

                if computed_result is None:
                    conn.send('NOT FOUND'.encode())
                    continue

                conn.send(str(computed_result).encode(self.format))

        print("[Server Thread]: Client disconnected!")
        conn.close()

    def start(self):
        """
        Start the server and listen for client connections
        """
        self.server_socket.listen()

        # enter an infinite loop to listen for client connections
        try:
            while True:
                conn, addr = self.server_socket.accept()
                # create an event for signaling when to stop the thread
                running = threading.Event()
                running.set()
                # create a new thread for the client
                thread = threading.Thread(
                    target=self.handle_client,
                    args=(conn, addr, running)
                )

                # append the thread to the list of threads
                self.threads.append(thread)
                # start the thread
                thread.start()
        
        # if the server is stopped by the user using Ctrl+C
        except KeyboardInterrupt:
            print("[Server]: Stopped by Ctrl+C")
        
        # close the server socket and join all threads
        finally:
            self.server_socket.close()
            for thread in self.threads:
                thread.join(timeout=2)

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
