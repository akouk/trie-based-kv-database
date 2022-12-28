import argparse
import socket
import random
import json


# Function that gets the command line arguments and convert them to the appropriate data types
def parse_KVClient_arguments():
    kvClient_parser = argparse.ArgumentParser(description="Key-Value Store: KV Client Parser")
    kvClient_parser.add_argument("-s", type=str, required=True, help="File containing a space-separated list of server IPs and ports")
    kvClient_parser.add_argument("-i", type=str, required=True, help="File containing data, that are output from dataCreation.py")
    kvClient_parser.add_argument("-k", type=int, required=True, help="Replication factor")
    kvClient_args = kvClient_parser.parse_args()
    return kvClient_args

kvClient_args = parse_KVClient_arguments()

#-------To create a client that connects to servers specified in a .txt file, you will need to use a programming language that supports network sockets, such as Python
# Funtion that parses the server file to get a list of server IPs and ports
def readServerFileAndStoreIPsAndPorts(serverfile):
    servers = []
    # Read server IPs and ports from the server file
    with open(serverfile, "r") as serverfile:
        serverFile_lines = serverfile.readlines()

        for each_line in serverFile_lines:
            # Check if the line contains two parts (key and data type)
            if len(each_line.strip().split(" ")) == 2:
                ip, port = each_line.strip().split()
                servers.append((ip, int(port)))
            else:
                # Skip the current iteration of the loop if the line does not contain two parts and ignore that line
                continue
    return servers

servers = readServerFileAndStoreIPsAndPorts(kvClient_args.s)


def connect_to_all_servers(servers):
    client_sockets = []

    for server_ip, server_port in servers:

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_ip, server_port))
        client_sockets.append(client_socket)

    return client_sockets



def send_data_to_randomly_chosen_servers(servers, data, replication_factor):
    client_sockets = connect_to_all_servers(servers)

    for each_data in data:
        chosen_servers = random.sample(client_sockets, replication_factor)

        for chosen_server in chosen_servers:
            # Send the PUT request to the server
            chosen_server.sendall(b"PUT " + each_data)
            # Recieve the response from the server
            put_response = chosen_server.recv(1024).decode()
            if put_response == b"OK":
                print(f"Data indexed successfully on server {chosen_server}")
            elif put_response == b"ERROR":
                print(f"Error indexing data on server {chosen_server}")

            # Close the connection to the server
            chosen_server.close()


def read_dataFile_and_put_data_to_servers(dataFile, client_sockets, replication_factor):

    with open(dataFile, "r") as dataFile:

        dataFile_lines = dataFile.readlines()

        for each_line in dataFile_lines:
            data = json.loads(each_line)

            send_data_to_randomly_chosen_servers(data, client_sockets, replication_factor)

    
read_dataFile_and_put_data_to_servers(kvClient_args.i, kvClient_args.k)


def send_the_GET_request_to_each_server_and_store_response(servers, key, replication_factor):
    get_results = []

    client_sockets = connect_to_all_servers(servers)

    # Set the number of down servers to 0
    down_servers = 0

    for server in client_sockets:

        # Send the GET request to the server
        get_request = f"GET {key}\n"
        server.sendall(get_request.encode())

        # Recieve the response from the server
        get_response = server.recv(1024).decode()

        if get_response == "OK":
            continue
        elif get_response == "ERROR":
            print("There was a problem with the GET request.\Get operation unsuccessful.")
            return
        else:
            down_server = check_if_the_server_is_down(server)
            if down_server == 1:
                down_servers += 1


        # Add the response to the results list
        get_results.append(get_response)
        # Close the connection to the server
        server.close()
    

    if get_results:
        if down_servers >= replication_factor:
            print(f"Warning: {replication_factor} or more servers are down. The correct output cannot be guaranted")
        else:
            print("GET request was successful")
        print("\n".join(get_results))
    else:
        print(f"NOT FOUND. The {key} is not a high-level key. Please provide a valid key")



def check_if_the_server_is_down(server):

    # Send PING request to server
    ping_request = "PING\n"
    server.send(ping_request.encode())

    # Set a timeout for the response
    server.settimeout(1)

    try:
        # Recieve response
        recieved_response = server.recv(1024).decode()
        if recieved_response == "PONG":
            down_server = 0
    except socket.timeout:
        # If no response is recieved within timeout, consider the server to be down
        down_server = 1
        # return
    return down_server
    


def delete_key(servers, key):
    client_sockets = connect_to_all_servers(servers)

    for server in client_sockets:
        # Send delete request to server
        delete_request = f"DELETE {key}\n"
        server.send(delete_request.encode())

        delete_response = server.recv(1024).decode()
        if delete_response == "OK":
            continue
        elif delete_response == "ERROR":
            print("There was a problem with the DELETE request.\nDelete operation unsuccessful.")
            return
        else:
            down_server = check_if_the_server_is_down(server)
            if down_server == 1:
                print("Invalid response from server.\nDelete cannot be reliably executed because one or more servers are down")
            return

        # Close the connection to the server
        server.close()

    print("Delete operation successful!")

def query(servers, key_path, replication_factor):
    client_sockets = connect_to_all_servers(servers)

    subkey_value = None
    down_servers = 0

    for client_socket in client_sockets:
        # Send QUERY request to server
        query_request = f"QUERY {key_path}\n"
        client_socket.send(query_request.encode())

        # Recieve response from server
        query_response = client_socket.recv(1024).decode()

        if query_response == "OK":
            subkey_value = query_response.split()[1]
            continue
        elif query_response == "ERROR":
            print("There was a problem with the QUERY request.\nQuery operation unsuccessful.")
        else:
            down_server = check_if_the_server_is_down(client_socket)
            if down_server == 1:
                down_servers += 1
    
    if subkey_value is not None:
        if down_servers >= replication_factor:
            print(f"Warning: {replication_factor} or more servers are down. The correct output cannot be guaranteed")
        else:
            print("QUERY request was successful")
        print("{}: {}").__format__(key_path, subkey_value)
    else:
        print(f"NOT FOUND. The {key_path} is not found. Please provide a valid keypath")

def compute(servers, key, function):
    client_sockets = connect_to_all_servers(servers)
    
    # Send a query request to all the servers with the extracted key
    query_results = []

    for client_socket in client_sockets:
        client_socket.send(f"QUERY {key}".encode())

        query_response = client_socket.recv(1024).decode()

        if query_response != "NOT FOUND":
            query_results.append(query_response)
    
    # Process the results
    computed_result = None
    for result in query_results:
        # Extract the value from the result
        computed_value = result.split(" -> ")[1].strip()

        # Perform the operation on the operand and the value
        if "-" in function:
            computed_result = int(function.split("-")([0]) - int(computed_value))
        elif "+" in function:
            computed_result = int(function.split("+")([0]) + int(computed_value))
        elif "*" in function:
            computed_result = int(function.split("*")([0]) * int(computed_value))
        elif "/" in function:
            computed_result = int(function.split("/")([0]) / int(computed_value))
    
    print(computed_result)



# def check_command(command):
#         # Parse command and key
#     parts = command.strip().split
#     if len(parts) !=2:
#         print("Error: Invalid command")
#         # continue
#     cmd, key = parts



def accept_input_from_user():

    command = input("Enter command (GET, DELETE, QUERY, COMPUTE or EXIT): ")

    while command.startswith != "EXIT":

        # Handle EXIT command
        if command.startswith == "EXIT":
            break

        # Handle GET command
        if command.startswith == "GET":
            key = command.split()[1]
            send_the_GET_request_to_each_server_and_store_response(servers, key, kvClient_args.k)
        
        # Handle DELETE command
        if command.startswith == "DELETE":
            key = command.split()[1]
            delete_key(servers, key)


        # Handle QUERY command
        if command.startswith == "QUERY":
            key_path = command.split()[1]
            query(servers, key_path, kvClient_args.k)



        # Handle COMPUTE command
        if command.startswith == "COMPUTE":
            # Parse the input to extract the function and the keypath
            function, keypath = command.split("WHERE")
            function = function.strip().split()[1]
            key = keypath.strip().split()[1]

            compute(servers, key, function)






# def connect_to_all_servers(servers):
#     # Connect to all servers
#     for ip, port in servers:
#         sockets = [socket.create_connection((ip, port))]
#         check_that_at_least_k_servers_are_available(sockets, kvClient_args.k)

# def check_that_at_least_k_servers_are_available(sockets, replication_factor):
#     # Check that at least k servers are available
#     if len(sockets) < replication_factor:
#         print(f"Error: At least {replication_factor} servers are requiered but only {len(sockets)} are available")
#         exit(1)


# def select_random_servers(servers, replication_factor):
#     selected_servers = random.sample(range(len(servers)), replication_factor)
#     return selected_servers

# def intantiate_client_socket():
#     client_socket = socket.socket()  # instantiate





# def put_data_to_random_servers(servers, replication_factor, dataFile):

#     client_socket = socket.socket()

#     connect_to_all_servers(servers)
#     selected_servers = select_random_servers(servers, replication_factor)



#     # Iterate over each server address in the .txt file
#     for server_address in selected_servers:

#         for ip, port in server_address:
            
#             # Connect to the server
#             client_socket.connect((ip, port))

#             with open(dataFile, "r") as dataFile:

#                 dataFile_lines = dataFile.readlines()

#                 for each_line in dataFile_lines:
#                     data = json.loads(each_line)

#                     # Send the PUT request to the server
#                     client_socket.sendall(b"PUT " + data)

#                     # Recieve the response from the server
#                     response = client_socket.recv(1024).decode()
#                     if response == b"OK":
#                         print("Data indexed successfully on server {}:{}".format(ip, port))
#                     elif response == b"ERROR":
#                         print("Error indexing data on server {}:{}".format(ip, port))
#                     # Clese the connection to the server
#                     client_socket.close()

# put_data_to_random_servers(servers, kvClient_args.k, kvClient_args.i)


# # client_socket.connect((host, port))  # connect to the server

# message = input(" -> ")  # take input

# while message.lower().strip() != 'bye':
#     client_socket.send(message.encode())  # send message
#     data = client_socket.recv(1024).decode()  # receive response

#     print('Received from server: ' + data)  # show in terminal

#     message = input(" -> ")  # again take input

# client_socket.close()  # close the connection


# if __name__ == '__main__':
#     client_program()
