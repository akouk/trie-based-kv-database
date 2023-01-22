import json 
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
        """
        Constructor method for the Client class
        :param servers_files_path: file path of the servers
        :param server_data: data that will be sent to the servers
        :param k: number of servers to connect to
        """
        self._servers_with_data = [] 
        self.k = k 
        self.servers_files_path = servers_files_path
        self.active_servers = self.get_online_servers() 
        self.data = self.get_data(server_data) 
        asyncio.run(self.put_request()) # run the put_request method asynchronously

    @property # this is a decorator that makes servers_with_data a read-only property
    def servers_with_data(self):
        return self._servers_with_data

    @servers_with_data.setter
    def servers_with_data(self, v: tp.List[socket.socket]) -> None:
        self._servers_with_data = v

    async def communication(self, server: socket.socket, command: str):
        server.send(command.encode('utf-8'))
        response = server.recv(5000).decode('utf-8')
        print(response)

    async def validate_active_servers(self, servers: tp.List[socket.socket]):
        active_servers = []
        for server in servers:
            try:
                server.send('ping'.encode('utf-8'))
                response = server.recv(5000).decode('utf-8')
                if response.lower() != 'pong':
                    continue
                active_servers.append(server)

            except:
                server.close()

        if not active_servers:
            print("All server are down, close the connection!")
            raise OSError()

        if len(active_servers) < self.k:
            print(f"Number of server is less than k:{self.k}")

        return active_servers

    async def listen(self):
        """
        Asynchronous method that listens for user input and sends commands to the servers
        """
        try:
            while True:

                command = input(
                    'Enter command (GET, DELETE, QUERY, COMPUTE or EXIT): '
                )
                if command.lower().startswith('get'):
                    servers = await self.validate_active_servers(self.active_servers)

                    await asyncio.gather(
                        *[
                            self.communication(server, command) # call the communication method for each server with the given command
                            for server in servers # iterate over the list of connections
                        ]
                    )

                elif command.lower().startswith('delete'):
                    servers = await self.validate_active_servers(self.active_servers)
                    if len(servers) != len(self.active_servers):
                        print('Delete can not be executed!')
                        continue
                    await asyncio.gather(
                        *[
                            self.communication(server, command)
                            for server in servers
                        ]
                    )

                elif command.lower().startswith('query'): 
                    servers = await self.validate_active_servers(self.active_servers)
                    await asyncio.gather(
                        *[
                            self.communication(server, command)
                            for server in servers
                        ]
                    )

                elif command.lower().startswith('compute'): 
                    await asyncio.gather(
                        *[
                            self.communication(server, command)
                            for server in self.active_servers
                        ]
                    )

                elif command.lower().startswith('exit'):
                    await asyncio.gather(
                        *[
                            self.communication(server, command)
                            for server in self.active_servers
                        ]
                    )
                    break

                else:
                    print(
                        'Your command must be one of the following: GET, DELETE, QUERY, COMPUTE or EXIT'
                    )

        except (KeyboardInterrupt, Exception) as error:
            server = await self.validate_active_servers(self.active_servers)
            
            await asyncio.gather(
                *[
                    self.communication(server, 'exit')
                    for server in server
                ]
            )

    def get_online_servers(self) -> tp.List[socket.socket]:
        """
        Method for getting the online servers
        :param path: file path of the servers
        :return: list of online servers
        """
        servers = [] 
        down_servers = [] 
        with open(self.servers_files_path, 'r') as f:
            server_file_lines = [line.rstrip('\n') for line in f] 

        for line in server_file_lines:
            ip, port = line.split(' ') 
            try:
                connection = self.connect_server(ip, int(port)) 
                servers.append(connection) 

            except (socket.error, ValueError):
                down_servers.append((ip, port))

        if down_servers:
            raise OSError(f'Following servers are down: {down_servers}')

        return servers 

    def connect_server(self, host: str, port: int) -> socket.socket:
        """
        Method for connecting to a server
        :param server: the server to connect to
        :return: the socket used to connect to the server
        """
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        client_socket.connect((host, port))
        return client_socket 

    def get_data(self, path: str) -> tp.List[tp.Dict[str, tp.Any]]:
        """
        Method for reading data from a file
        :param path: file path of the data
        :return: the data as a dictionary
        """
        with open(path, 'r') as f: 
            server_file_lines = [json.loads(line.rstrip('\n')) for line in f] 
        return server_file_lines

    async def put_request(self):
        """
        Asynchronous method that puts the data to random k selected servers
        """
            
        self.servers_with_data = random.sample(self.active_servers, k=self.k) 
        for server in self.servers_with_data:
            for data in self.data:
                msg = 'PUT ' + json.dumps(data)
                server.send(msg.encode('utf-8')) 
                response = server.recv(5000).decode('utf-8') 
                if response.lower() != 'ok': 
                    await asyncio.gather(
                        *[
                            self.communication(server, 'exit')
                            for server in self.active_servers
                        ]
                    )
                    raise OSError('Failed to send the data') 


def run_client_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-s',
        help='Server file',
        type=txt_file,
        required=True
    )
    parser.add_argument(
        '-i',
        help='data to index',
        type=txt_file,
        required=True
    ) 
    parser.add_argument(
        '-k',
        help='replication factor',
        type=int_type,
        required=True
    ) 
    args = parser.parse_args() 
    return args


def txt_file(arg):
    if not os.path.isfile(arg):
        raise argparse.ArgumentTypeError(
            f'Error: {arg} does not exist. Please provide an existing file!')
    elif not os.path.splitext(arg)[1] == '.txt': 
        raise argparse.ArgumentTypeError(
            f'Error: {arg} is not a text file. Please provide a txt file as argument!')
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
