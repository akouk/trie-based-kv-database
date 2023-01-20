# Distributed, fault-tolerant, Key:Value Database

This is a distributed, fault-tolerant, key-value database implementation that allows clients to connect with multiple servers to store and retrieve data. The key-value pairs are stored in a Trie data structure and the servers use a consensus algorithm to ensure data consistency.


This project includes a client script that connects to the servers, sends data to the servers using 'pu' command, and listens for user input to perform 'get', 'delete', 'query' and 'compute' commands.


The key-value database project consists of two programs: a Key-Value client and a Key-Value server. The Key-Value client is responsible for accepting queries from the user and forwarding them to the Key-Value servers, collecting the results and presenting them to the user. The Key-Value servers are responsible for storing the actual data and handling queries from the client.



## Usage
The Trie-based key-value database allows the user to store, retrieve, delete, query and compute mathematical expressions using a trie data structure. The system is composed of a client and multiple servers. The client is responsible for sending commands to the servers, while the servers are responsible for storing and processing the data. The system uses Trie data structure to store the key-value pairs, making it efficient for querying and computing mathematical expression.


## Running the project

### Running the servers
To run the project, you need to start the servers first. Each server runs on a separate script. Use the following command to run the servers:
```python
python3 run_kv_server.py -p <port> -a <ip_address>
```

#### Parameters

- '-p': the port of the server
- '-a': the ip address of the server


## Running the client
To run the client, use the following command:
```python
python3 run_kv_client.py -s <servers_file_path> -i <server_data> -k <replicator_factor>
```
#### Parameters
- '-s': file path of the servers
- '-i': data that will be sent to the servers
- '-k': number of servers to send the data  

Once the script is running, it will connect to the number of servers specified by the 'k' argument, read the data specified by the 's' arguments, and send a 'PUT' request with tha data to servers.

The client will then listen for input and take these commands:
- GET <key> : retrieves the value of the specified key
- DELETE <key> : deletes the key-value pair of the specified key
- QUERY <keypath> : retrieves key-value pairs (or values) of the specified key path
  COMPUTE <expression> : computes a mathematican expression
  EXIT: closses the connection
  
  
## RNotes
- Make 








## Key-Value Client
To start the Key-Value client, use the following command:
python3 kvClient.py -s serverFile.txt -i dataToIndex.txt -k 2

Where:
- "serverFile.txt" is a space separated list of servers IPs and their respective ports that will be listening for queries and indexing commands
- "dataToIndex.txt" is a file containg data
- "k" is the replication factor, i.e. how many different servers will have the same replicated data

Once the Ley-Value client starts, it connects to all the servers and sends requests to store tha data from "dataToIndex.txt". If everything is successful, the servers will respond with "OK", or "ERROR" if there was a problem.

After the indexing process is complete, the Key-Value client can accept the following commands:
- "GET key": queries all servers for the data with the given key, and prints the results if found
- "DELETE key": deletes the specified key. This command needs to be forwarded to all the servers. If any server is down, delete cannot be reliably executed.
- "QUERY keypath": similar to "GET", but returns the value of a subkey within a value
- "COMPUTE : 
-
The Key-Value clients will continue to work unless k servers are down. If k or more servers are down, the client will output a warning indicating it cannot guarantee the correct output.



