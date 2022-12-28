import argparse
import os
import random
import string
import json

# Function that gets the command line arguments and convert them to the appropriate data types
def parse_dataCreation_arguments():
    dataCreation_parser = argparse.ArgumentParser(description="Data Creation")
    dataCreation_parser.add_argument("-k", type=str, required=True, help="File containing a space-separated list of key names and their data types")
    dataCreation_parser.add_argument("-n", type=int, required=True, help="Number of lines (i.e. separate data) to generate")
    dataCreation_parser.add_argument("-d", type=int, required=True, help="Maximum level of nesting")
    dataCreation_parser.add_argument("-l", type=int, required=True, help="Maximum length of a string value")
    dataCreation_parser.add_argument("-m", type=int, required=True, help="Maximum number of keys inside each value")
    dataCreation_args = dataCreation_parser.parse_args()
    return dataCreation_args

dataCreation_args = parse_dataCreation_arguments()

# This code will first check if the file has a .txt extension. 
# If it is .txt extension it will generate the data
# If it does not, it will raise a Value Error exception with the message "File is not a text file"
# If the file does not exist, it will raise a FileNotFoundError exception with the message "File does not exist"
def check_if_file_is_correct(keyfile):    
    try:
        # Check if the file has a .txt extension
        if os.path.splitext(keyfile)[1] == ".txt":
            # Call the genData() function to generate the data
            generate_and_write_data_to_file(dataCreation_args.n, dataCreation_args.d, dataCreation_args.m, dataCreation_args.l, dataCreation_args.k)
        else:
            raise ValueError("File is not a text file.")
    except FileNotFoundError:
        print("File does not exist. Plase provide an existing file!")
    except ValueError as e:
        print(e)


# Function that reads the given keyFile.txt and stores each lines key and its data type in a dictionary
def read_keyFile_and_store_keys_and_their_data_types(keyFile):
    keyFile_dict = {}

    # Open the file and read its lines
    with open(keyFile, "r") as keyFile:
        lines = keyFile.readlines()

        # Read each line of the file and store the key and its data type in the dictionary
        for each_line in lines:

            # Check if the line contains two parts (key and data type)
            if len(each_line.strip().split(" ")) == 2:
                key_name, data_type = each_line.strip().split()
                keyFile_dict[key_name] = data_type
            else:
                # Skip the current iteration of the loop if the line does not contain two parts and ignore that line
                continue
        
    # Return the dictionary
    return keyFile_dict





# Function that generates random string value (combination of letters and number) up to the specified length by -l parameter 
def generate_random_string(max_string_length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k = max_string_length))

# Function that generates random integer within a specified range
def generate_random_integer(min_value, max_value):
    return random.randint(min_value, max_value)

# Function that generates random float within a specified range
def generate_random_float(min_value, max_value):
    return random.uniform(min_value, max_value)

# Function that generates random value
def generate_random_value(data_type, max_string_length):
    if data_type == "string":
        return generate_random_string(max_string_length)
    elif data_type == "int":
        return generate_random_integer(0,100)
    elif data_type == "float":
        return generate_random_float(0.0,100.0)


        
def generate_random_KeyValue_pair(num_lines, max_nesting, max_keys, max_string_length, keyFile_dict):
    random_data = {}

    # Generate a random number of keys up to the maximum specified by the -m parameter
    num_keys = random.randint(1, max_keys)
    
    for i in range(num_keys):
        key = random.choice(list(keyFile_dict.keys()))
        dataType = keyFile_dict[key]
        # If the maximum level of nesting is 0, then its at the bottom level and random values can be generated for each key, up to the specified keys inside each value
        random_data[key] = generate_random_value(dataType, max_string_length)

        # If the maximum level of nesting is greater than 0, then a random number of keys for the current level of nesting can be generated, up to the specified keys inside each value
        # and the function can be called recursively, to generate the values of each these keys
        if max_nesting > 0:
            random_data[key] = generate_random_KeyValue_pair(num_lines, max_nesting-1, max_keys, max_string_length, keyFile_dict)

    return random_data


def generate_and_write_data_to_file(num_lines, max_nesting, max_keys, max_string_length, keyFile_dict):

    keyFile_dict = read_keyFile_and_store_keys_and_their_data_types(keyFile_dict)
    
    # If keyFile dictionary is empty, then return
    if not keyFile_dict:
        return

    with open("dataToIndex.txt", "w") as generated_file:

        for i in range(num_lines):
            generated_data = generate_random_KeyValue_pair(num_lines, max_nesting, max_keys, max_string_length, keyFile_dict)

            for key, value in generated_data.items():
                generated_file.write(json.dumps({key: value}) + "\n")

    generated_file.close()