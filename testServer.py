import argparse
import socket


class TrieNode:
    def __init__(self):
        self.children = {} # a dictionary mapping characters to child nodes
        self.value = None # the value stored at this node (if any)
        self.is_deleted = False # a flag indicating whether the node has been deleted

    def remove_if_unused(self):
        # remove the node if it has no children and is marked as deleted
        if self.is_deleted and not self.children:
            del self

class Trie:
    def __init__(self):
        self.root = TrieNode() # create the root node of the trie

    def put(self, key, value):
        # start at the root of the trie
        current_root = self.root

        # follow the path of the key in the trie, creating new nodes as needed
        for c in key:
            if c not in current_root.children:
                current_root.children[c] = TrieNode()
            current_root = current_root.children[c]
        
        #store the value at the final node
        current_root.value = value
    
    def get(self, key):
        # start at the root of the trie
        current_root = self.root
        # follow the path of the key in the trie, creating new nodes as needed
        for c in key:
            if c not in current_root.children:
                # the key does not exist in the trie
                return None
            current_root = current_root.children[c]
        
        # return the value at the end of the path if the node is not deleted
        if not current_root.is_deleted:
            return current_root.value
        else:
            return None

    def delete(self, key):
        # start at the root of the trie
        current_root = self.root
        # follow the path of the key in the trie, creating new nodes as needed
        for c in key:
            if c not in current_root.children:
                # the key is not in the trie
                return
            current_root = current_root.children[c]
        
        # mark the note at the end of the path as deleted
        current_root.is_deleted = True
    
    def query(self, keypath):
        # split the keypath into individual keys
        keys = keypath.split(".")

        # start at the root of the trie
        current_root = self.root

        # follow the path of the keys in the trie
        for key in keys:
            if key not in current_root.children:
                # the key is not in the trie
                return None
            current_root = current_root.children[key]

        # return the value or the subkey at the end of the path (if any)
        if current_root.value is not None:
            return current_root.value
        else:
            return current_root.children

    def compute(self, formula, variables):
        # define a dictionary of operator functions
        operators = {
            "+": lambda x, y: x + y,
            "-": lambda x, y: x - y,
            "*": lambda x, y: x * y,
            "/": lambda x, y: x / y,
            "^": lambda x, y: x **y
        }

        # initialize the result to the first value in the formula
        result = variables[formula[0]]

        # loop through the formula, applying the appropriate operator function to the result and the next value
        for i in range(1, len(formula), 2):
            op = formula[i]
            val = variables[formula[i+1]]
            result = operators[op](result, val)

        return result


class KVServer:
    def server_initialization(self, ip_address, port):
        self.ip_address = ip_address
        self.port = port
        self.root = Trie()

    #receive the query from the client
    def accept_connection_from_client(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # this function takes two arguments: the address family (AF_INET for IPv4 and AF_INET6 for IPv6) and the type of socket (SOCK_STREAM for TCP socket)
        self.server_socket.bind((self.ip_address, self.port))
        # configure how many client the server can listen simultaneously
        self.server_socket.listen(1) # listen for incoming connections

        # accept a connection from the client
        connection, client_address = self.server_socket.accept()   # accept new connection
        
        return connection, client_address

    def put_request(self, key, value):
        #Trie.put(key, value)
        self.root.put(key, value) # insert the key-value pair into the trie

    def get_request(self, key):
        #value = Trie.get(key)
        return self.root.get(key) # retrieve the value associated with the key from the trie


    def delete_request(self, key):
        #Trie.delete(key)
        self.root.delete(key) # delete the key and its associated value from the trie

    def query_request(self, keypath):
        #
        # result = Trie.query(keypath)
        return self.root.query(keypath) # retrieve the value or subkey associated with the keypath from the trie

            
    def compute_request(self, formula, variables):
        # Parse the formula and retrieve any required values from the key-value store
        #result = eval(formula, variables) # Compute the redult of the formula
        #return result
        return self.root.compute(formula, variables) # compute formula using values from the trie

# Function that gets the command line arguments and convert them to the appropriate data types
def parse_KVServer_arguments():
    kvServer_parser = argparse.ArgumentParser(description="Key-Value Sptre: KV Server Parser")
    kvServer_parser.add_argument("-a", type=str, required=True, help="IP address")
    kvServer_parser.add_argument("-p", type=str, required=True, help="Port")
    kvServer_args = kvServer_parser.parse_args()
    return kvServer_args

kvServer_args = parse_KVServer_arguments()


def main():
    server = KVServer(kvServer_args.a, kvServer_args.p)
    connection, client_address = KVServer.accept_connection_from_client()
    print("Connection from: " + str(client_address))

    while True:
        client_request = connection.recv(1024).decode() #receive the request from the client

        if not client_request:
            # if data is not received break
            break

        command, args = parse_received_input_command(client_request) # parse the request to determine the command and arguments
        if command == "GET":
            if len(args) == 1:
                result = server.get_request(args[0])
            else:
                print("Error: Invalid command")
        elif command == "DELETE":
            if len(args) == 1:
                result = server.delete_request(args[0])
            else:
                print("Error: Invalid command")
        elif command == "QUERY":
            if len(args) == 1:
                result = server.query_request(args[0])
            else:
                print("Error: Invalid command")
        elif command == "COMPUTE":
            result = server.compute_request(args[0], args[1])
        else:
            result = "ERROR: Invalid command"

        connection.send(result.encode())  # send data to the client
    # close the connection and return the received request
    connection.close()


def parse_received_input_command(input_cmd):
    # split the query into tokens
    tokens = input_cmd.split()

    # extract the command and arguments
    command = tokens[0]
    args = tokens[1:]

    return command, args



# # get the hostname
# host = socket.gethostname()
# port = 5000  # initiate port no above 1024

# server_socket = socket.socket()  # get instance
# # look closely. The bind() function takes tuple as argument
# server_socket.bind((host, port))  # bind host address and port together


# # configure how many client the server can listen simultaneously
# server_socket.listen(2)
# conn, address = server_socket.accept()  # accept new connection
# print("Connection from: " + str(address))
# while True:
#     # receive data stream. it won't accept data packet greater than 1024 bytes
#     data = conn.recv(1024).decode()
#     if not data:
#         # if data is not received break
#         break
#     print("from connected user: " + str(data))
#     data = input(' -> ')
#     conn.send(data.encode())  # send data to the client

# conn.close()  # close the connection


if __name__ == '__main__':
    main()