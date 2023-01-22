import json # import the json module
import socket # import the socket module
import random # import the random module
import asyncio # import the asyncio module
import typing as tp # import the typing module and give it the alias tp
import argparse # import the argparse module
import os # import the os module


class Client: # define the class Client
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
        self._servers_with_data = [] # create an empty list for servers_with_data
        self.k = k # assign k to the object's k attribute
        self.servers_files_path = servers_files_path
        self.active_servers = self.get_online_servers() # get online servers
        self.data = self.get_data(server_data) # read the server data
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
                # take input
                command = input(
                    'Enter command (GET, DELETE, QUERY, COMPUTE or EXIT): '
                )
                if command.lower().startswith('get'): # check if command starts with "get"
                    servers = await self.validate_active_servers(self.active_servers)

                    await asyncio.gather(
                        *[
                            self.communication(server, command) # call the communication method for each server with the given command
                            for server in servers # iterate over the list of connections
                        ]
                    )

                elif command.lower().startswith('delete'): # check if command starts with "delete"
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

                elif command.lower().startswith('query'): # check if command starts with "query"
                    servers = await self.validate_active_servers(self.active_servers)
                    await asyncio.gather(
                        *[
                            self.communication(server, command)
                            for server in servers
                        ]
                    )

                elif command.lower().startswith('compute'): # check if command starts with "compute"
                    await asyncio.gather(
                        *[
                            self.communication(server, command)
                            for server in self.active_servers
                        ]
                    )

                elif command.lower().startswith('exit'): # check if command starts with "exit"
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
        servers = [] # Create an empty list to store online servers
        down_servers = [] # Create an empty list to store down servers
        with open(self.servers_files_path, 'r') as f:
            server_file_lines = [line.rstrip('\n') for line in f] # Open the file and read each line of the file, stripping the newline character

        for line in server_file_lines:
            ip, port = line.split(' ') # Split the line into ip and port
            try:
                connection = self.connect_server(ip, int(port)) # Connect to the server using the ip and port
                servers.append(connection) # Append the server to the servers list

            except (socket.error, ValueError):
                down_servers.append((ip, port))

        if down_servers:
            raise OSError(f'Following servers are down: {down_servers}')

        return servers # Return the list of online servers

    def connect_server(self, host: str, port: int) -> socket.socket:
        """
        Method for connecting to a server
        :param server: the server to connect to
        :return: the socket used to connect to the server
        """
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create a socket object
        client_socket.connect((host, port)) # Connect to the server using the ip and port attributes of the server object
        return client_socket # Return the socket object used to connect to the server

    def get_data(self, path: str) -> tp.List[tp.Dict[str, tp.Any]]:
        """
        Method for reading data from a file
        :param path: file path of the data
        :return: the data as a dictionary
        """
        with open(path, 'r') as f: # Open the file
            server_file_lines = [json.loads(line.rstrip('\n')) for line in f] # Read each line of the file, stripping the newline character and convert json to dict
        return server_file_lines # Return list of dict

    async def put_request(self):
        self.servers_with_data = random.sample(self.active_servers, k=self.k) # assign a random sample of self.active_servers to servers_with_data
        for server in self.servers_with_data:
            for data in self.data:
                msg = 'PUT ' + json.dumps(data) # create message with format 'PUT' + json serialized data
                server.send(msg.encode('utf-8')) # send the message to the server, encoded as utf-8
                response = server.recv(5000).decode('utf-8') # receive response from the server, with a buffer size of 5000 and decode it
                if response.lower() != 'ok': # check if the response is not 'ok'
                    # Close the connection with active servers
                    await asyncio.gather(
                        *[
                            self.communication(server, 'exit')
                            for server in self.active_servers
                        ]
                    )
                    raise OSError('Failed to send the data') # raise an OSError if the response is not 'ok'


def run_client_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-s',
        help='Server file',
        type=txt_file,
        required=True
    ) # add the -s argument as the server file, which is required and should be a txt file
    parser.add_argument(
        '-i',
        help='data to index',
        type=txt_file,
        required=True
    ) # add the -i argument as the data file, which is required and should be a txt file
    parser.add_argument(
        '-k',
        help='replication factor',
        type=int_type,
        required=True
    ) # add the -k argument as the replication factor, which is required and should be an integer
    args = parser.parse_args() # parse the arguments passed
    return args


def txt_file(arg):
    if not os.path.isfile(arg): # check if the file exists
        raise argparse.ArgumentTypeError(
            f'Error: {arg} does not exist. Please provide an existing file!')
    elif not os.path.splitext(arg)[1] == '.txt': # check if the file is a txt file
        raise argparse.ArgumentTypeError(
            f'Error: {arg} is not a text file. Please provide a txt file as argument!')
    return arg


def int_type(arg):
    if not arg.isdigit(): # check if the argument is a digit
        raise argparse.ArgumentTypeError(
            f'Error: {arg} is not an integer. Please provide an integer as argument!')
    return int(arg)


def main():
    args = run_client_arguments() # get the arguments
    client = Client(args.s, args.i, args.k) # create a client object with the given arguments
    asyncio.run(client.listen()) # run the listen method asynchronously


if __name__ == '__main__':
    main()


# python3 run_kv_client.py -s server_file.txt -i output_file.txt -k 2
