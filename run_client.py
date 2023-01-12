import json
import NEW.BaseServer as BaseServer
import socket
import random
import asyncio
import typing as tp
import argparse
import os


class Client:
    def __init__(
        self,
        servers_files_path: str,
        server_data: str,
        k: int
    ) -> None:
        self.k = k
        self.active_servers = self.get_online_servers(servers_files_path)
        if len(self.active_servers) < k:
            raise OSError(f'The number of servers is less than {k}')
        self.connections = list(map(self.connect_server, self.active_servers))
        self.data = self.get_data(server_data)
        self.put_request()
        self._servers_with_data = []

    @property
    def servers_with_data(self):
        return self._servers_with_data

    async def communication(self, server: socket.socket, command: str):
        server.send(command.encode('utf-8'))
        response = server.recv(5000).decode('utf-8')
        print(response)

    async def listen(self):
        # take input
        command = input(
            'Enter command (GET, DELETE, QUERY, COMPUTE or EXIT): '
        )

        while not command.lower().startswith('exit'):
            if command.lower().startswith('get'):
                # GET HERE
                await asyncio.gather(
                    *[
                        self.communication(server, command)
                        for server in self.connections
                    ]
                )

            elif command.lower().startswith('delete'):
                # DELETE HERE
                ...

            elif command.lower().startswith('query'):
                # QUERY HERE
                ...

            elif command.lower().startswith('COMPUTE'):
                # GET COMPUTE
                ...

            elif command.lower().startswith('exit'):
                break

            else:
                print(
                    'Your command must be one of the (GET, DELETE, QUERY, COMPUTE or EXIT)'
                )
            command = input(
                'Enter command (GET, DELETE, QUERY, COMPUTE or EXIT): '
            )

    def get_online_servers(self, path: str) -> tp.List[BaseServer.BaseServer]:
        servers = []
        with open(path, 'r') as f:
            serverFile_lines = [line.rstrip('\n') for line in f]
        for line in serverFile_lines:
            ip, port = line.split(' ')
            skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                skt.connect((ip, int(port)))
                servers.append(BaseServer.BaseServer(
                    port=int(port), host=ip)
                )
            except socket.error:
                continue

        return servers

    def connect_server(self, server: BaseServer.BaseServer) -> socket.socket:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server.host, server.port))
        return client_socket

    def get_data(self, path: str) -> tp.List[tp.Dict[str, tp.Any]]:
        with open(path, 'r') as f:
            serverFile_lines = [json.loads(line.rstrip('\n'))for line in f]
        return serverFile_lines

    def put_request(self):
        self._servers_with_data = random.sample(self.connections, k=self.k)
        for server in self._servers_with_data:
            for data in self.data:
                msg = 'PUT ' + json.dumps(data)
                print(msg)
                server.send(msg.encode("utf-8"))
                response = server.recv(5000).decode('utf-8')

                if response.lower() != 'ok':
                    raise OSError('Failed to send the data')

def run_client_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s",
        help="Server file",
        type=txt_file,
        required=True
    )
    parser.add_argument(
        "-i",
        help="data to index",
        type=txt_file,
        required=True
    )
    parser.add_argument(
        "-k",
        help="replication factor",
        type=str,
        required=True
    )
    args = parser.parse_args()
    return args

def txt_file(arg):

    if not os.path.isfile(arg):
        raise argparse.ArgumentTypeError(f"Error: {arg} does not exist. Please provide an existing file!")
    elif not os.path.splitext(arg)[1] == ".txt":
        raise argparse.ArgumentTypeError(f"Error: {arg} is not a text file. Please provide a txt file as argument!")
    return arg

def int_type(arg):
    if not arg.isdigit():
        raise argparse.ArgumentTypeError(
            f'Error: {arg} is not an integer. Please provide an integer as argument!')
    return int(arg)


def main():
    args = run_client_arguments()
    client = Client(args.s, args.i, args.k)
    asyncio.run(client.listen())

if __name__ == '__main__':
    main()
    
    
