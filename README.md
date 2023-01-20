# Key-Value Database Program
The key-value database project consists of two programs: a Key-Value client and a Key-Value server. The Key-Value client is responsible for accepting queries from the user and forwarding them to the Key-Value servers, collecting the results and presenting them to the user. The Key-Value servers are responsible for storing the actual data and handling queries from the client.

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



