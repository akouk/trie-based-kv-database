# Distributed Trie-based Key:Value Database

This is a distributed, fault-tolerant, key-value database implementation that allows clients to connect with multiple servers to store and retrieve data. The key-value pairs are stored in a Trie data structure and the servers use a consensus algorithm to ensure data consistency.

The key-value database project consists of two programs: a Key-Value client and a Key-Value server. The Key-Value client is responsible for accepting queries from the user and forwarding them to the Key-Value servers, collecting the results and presenting them to the user. The Key-Value servers are responsible for storing the actual data and handling queries from the client.



## Usage
The Trie-based key-value database allows the user to store, retrieve, delete, query and compute mathematical expressions using a trie data structure. The system is composed of a client and multiple servers. The client is responsible for sending commands to the servers, while the servers are responsible for storing and processing the data. The system uses Trie data structure to store the key-value pairs, making it efficient for querying and computing mathematical expression.


## Running the project

### Running the servers
To run the project, you need to start the servers first. Each server runs on a separate script. Use the following command to run the servers:
```python
python3 run_kv_server.py <ip_address> -p <port> -a 
```

#### Parameters
- `-a` : the ip address of the server
- `-p` : the port of the server

Each server starts at the specified IP adress and port (which should be one from the server file that the client is accepting as input) and is waiting for queries. Once the query is received, the server parses the query. If the query is incorrent (e.g. missing) the server returns ERROR to the client together with a message describing the error. If the query is correct, the server looks up its internal data structures and attempts to find the data corresponding to the quety. If the data is found, it is returned. If the data is not found, then NOTFOUND is returned.

### Running the client
To run the client, use the following command:
```python
python3 run_kv_client.py -s <servers_file_path> -i <server_data> -k <replicator_factor>
```
#### Parameters
- `-s` : a space separated list of servers IPs and their respective ports that will be listening for queries and indexing commands
- `-i` : data that will be sent to the servers
- `-k` : replication factor, i.e. how many different servers will have the same replicated data

Once the client starts, it connects to all servers, and for each line in data file it randomly pick k servers where it sends a request of the form PUT data. Each of servers now stores (in-memory) the data that was sent over the socket. If everything was successful it should respond to the client with OK or ERROR if there was a problem.


## Input commands
Once the indexing process has completed, the client now expects from the keyboard one of the following commands:

| Command | Description |
| --- | --- |
| `GET key` | Retrieves the value of the specified high-level key |
| `DELETE key` | Deletes the specified high-level key |
| `QUERY keypath` | Retrieves the value of a subkey in the value part of the high-level path |
| `COMPUTE f(x) WHERE x = QUERY key.key2...` | Computes a simple computation with the values coming from a query to the KV Database |
| `COMPUTE f(x,y,z...) WHERE x = QUERY key1.key2 AND y = ... AND z = ...` | Computes an advanced computation with the values coming from a query to the KV Database |
| `EXIT` | Closes connection to servers |
  
  
## Examples

- Example of a server file:
```
127.0.0.1 4000
127.0.0.1 7000
127.0.0.1 9000
127.0.0.1 5000
```

- Example of data to be stored on the servers:
```python
{'key1': {'key2' : {'key3': 4, 'key4': 8}}}
{'key5': {'key6': 2, 'key7': 6}}
{'key8': {"key9': {'key10': {'key11': 3} , 'key12': {'key13': 7, 'key14': 11}, 'key15': {'key16': 5}}}}
```
  
  
- To retrieve the value of the `key5` enter the following command:
```python
GET key5
```
In this case, the data with the given high-level key (i.e. `key5`) is queried across all servers and if the results are found it is printed on the screen.
This example queries all four servers of the example above and print out the following:
```python
'key5' -> {'key6': 2, 'key7': 6}
```
Since it's implemented k-replication, the client continues to work unless k servers are down. If >= k servers are down the client outputs a warning indicating that k or more servers are down and therefore it cannot guarantee the correct output.

  
- To delete the `key5` enter the following command:
```python
DELETE key5
```
This command deletes the specified high-level key (i.e., `key5`), and is forwarded to all servers. If there is even one server down, delete cannot be
reliably executed and thus prints a message indicating that delete cannot happen.

  
- To retrieve value of key path `key1.key2` enter the following command:
```python
QUERY key1.key2
```

This command specifies that the key was not found if a query with a non-existent key wasasked. QUERY works in an identical way to GET as far as replication (i.e., number of available servers) is concerned. This exaple will print out the following:
```python
'key1.key2' -> {'key3': 4, 'key4': 8}
```
  
- To compute  a simple computatio with the value of key path `key5.key6` enter the following command:
```python
COMPUTE x+2 WHERE x = QUERY key5.key6
```
This implements basic arithmetic functions of addition, subtraction, division, multiplication and power. This exaple will print out the following:
```python
2
```


- To compute an advanced computation with the values coming from a query to the KV Store enter the following command:
```python
CMOPUTE x+2*(y+3) WHERE x = QUERY key1.key2.key3 AND y = QUERY key8.key9.key12.key14
```
This case is an extending of the COMPUTE operation to allow for more advanced computations. More variables are handling as well as precedence of the operators and parentheses. This exaple will print out the following:
```python
32
```
Trigonometric (sin, cos, tan) and logarithmic (base 10) functions are also recognized


