import argparse
import os
import random
import string
import json
import typing as tp

# chance to add [] value in key
EMPTY_DATA_CHANCE = 80


class ValueGenerator:

    # Function that generates random string value (combination of letters and number) up to the specified length by -l parameter 
    def generate_random_string(self, max_string_length: int) -> str:
        return ''.join(random.choices(string.ascii_letters + string.digits, k = max_string_length))

    # Function that generates random integer within a specified range
    def generate_random_integer(self, min_value: int, max_value: int) -> int:
        return random.randint(min_value, max_value)

    # Function that generates random float within a specified range
    def generate_random_float(self, min_value: float, max_value: float) -> float:
        return random.uniform(min_value, max_value)

    # Function that generates random value
    def generate_random_value(self, data_type: str, max_string_length: int, is_root: bool) -> tp.Type[tp.Union[str, int, float]]:

        random_int = self.generate_random_integer(0, 100)
        if random_int < EMPTY_DATA_CHANCE and is_root:
            return None
        elif data_type == "string":
            return self.generate_random_string(max_string_length)
        elif data_type == "int":
            return self.generate_random_integer(0,100)
        elif data_type == "float":
            return self.generate_random_float(0.0,100.0)


class KeyValuePairGenerator():
      
    def __init__(self, kv_dict: dict) -> None:
        self.kv_dict = kv_dict
        self.value_generator = ValueGenerator()
    

    def generate_random_KeyValue_pair(
        self,
        num_lines: int, 
        max_nesting: int, 
        max_string_length: int,
        max_keys: int,
        kv_dict: dict,
        is_root: bool
    ) -> tp.Dict[str, tp.Union[str, int, float, None, tp.Dict]]:

        random_data = {}

        # Generate a random number of keys up to the maximum specified by the -m parameter
        num_keys = random.randint(1, max_keys)

        value_generator = ValueGenerator()

        for i in range(num_keys):
            key = random.choice(list(kv_dict.keys()))
            data_type = kv_dict[key]

            if is_root:
                key += value_generator.generate_random_string(max_string_length)

            # If the maximum level of nesting is 0, then its at the bottom level and random values can be generated for each key, up to the specified keys inside each value
            random_data[key] = value_generator.generate_random_value(data_type, max_string_length, is_root)

            # If the maximum level of nesting is greater than 0, then a random number of keys for the current level of nesting can be generated, up to the specified keys inside each value
            # and the function can be called recursively, to generate the values of each these keys
            if max_nesting > 0 and random_data[key] != None:
                random_data[key] = self.generate_random_KeyValue_pair(
                    num_lines, 
                    max_nesting-1, 
                    max_string_length, 
                    max_keys,
                    kv_dict,
                    False
                )
                
        return random_data


class DataGenerator(KeyValuePairGenerator):
    def __init__(
        self, 
        input_key_file: str,
        num_lines: int,
        max_nesting: int,
        max_string_length: int,
        max_keys: int,
        file_to_generate_data: str
    ) -> None:

        self.input_key_file = input_key_file
        self.num_lines = num_lines
        self.max_nesting = max_nesting
        self.max_string_length = max_string_length
        self.max_keys = max_keys
        self.file_to_gerate_data = file_to_generate_data

        # Function that reads the given .txt file and stores each lines key and its data type in a dictionary
    def read_key_file(self, input_file: str) -> dict:
        key_dict = {}
        with open(self.input_file, 'r') as f:
            input_key_file_lines = [line.rstrip('\n') for line in f]

        for each_line in input_key_file_lines:
            try:
                key_name, data_type = each_line.strip().split()
                key_dict[key_name] = data_type
            except SyntaxError:
                print("Invalid Syntax. Each line must contain two parts: key and data type")

        # Return the dictionary
        return key_dict

    # Function that generates and writes the data to a file
    def generate_and_write_data_to_file(self) -> None:

        # Read the key file and store the keys and their data types in a dictionary
        self.kv_dict = self.read_key_file(self.input_key_file)

        with open(self.file_to_gerate_data, "w") as generated_file: # Open the output file for writing

            for _ in range(self.num_lines):
                # Generate a random key-value pair
                generated_data = self.generate_random_KeyValue_pair(
                    self.num_lines, 
                    self.max_nesting,
                    self.max_string_length,
                    self.max_keys,
                    self.kv_dict,
                    True
                )
                generated_file.write(json.dumps(generated_data) + "\n") # Write the data to the output file in JSON format

        generated_file.close() # Close the output file


def parse_dataCreation_arguments():
    dataCreation_parser = argparse.ArgumentParser(description="Data Creation Parser")
    dataCreation_parser.add_argument(
        "-k", 
        type=txt_file, 
        required=True, 
        help="File containing a space-separated list of key names and their data types"
    )
    dataCreation_parser.add_argument(
        "-n", 
        type=int_type, 
        required=True, 
        help="Number of lines (i.e. separate data) to generate"
    )
    dataCreation_parser.add_argument(
        "-d", 
        type=int_type, 
        required=True, 
        help="Maximum level of nesting"
    )
    dataCreation_parser.add_argument(
        "-l", 
        type=int_type, 
        required=True, 
        help="Maximum length of a string value"
    )
    dataCreation_parser.add_argument(
        "-m", 
        type=int_type, 
        required=True, 
        help="Maximum number of keys inside each value"
    )
    dataCreation_parser.add_argument(
        "-o",
        type=str,
        required=True,
        help="Name of the file to write the data"
    )
    dataCreation_args = dataCreation_parser.parse_args()
    return dataCreation_args

# This code will first check if the file has a .txt extension. 
def txt_file(arg):
    if not os.path.isfile(arg):
        raise argparse.ArgumentTypeError(f"Error: {arg} does not exist. Please provide an existing file!")
    elif not os.path.splitext(arg)[1] == ".txt":
        raise argparse.ArgumentTypeError(f"Error: {arg} is not a text file. Please provide a txt file as argument!")
    return arg

def int_type(arg):
    if not arg.isdigit():
        raise argparse.ArgumentTypeError(f"Error: {arg} is not an integer. Please provide an integer as argument!")
    return int(arg)


def main():
    dataCreation_args = parse_dataCreation_arguments()
    generate_data = DataGenerator(
        dataCreation_args.k, 
        dataCreation_args.n, 
        dataCreation_args.d, 
        dataCreation_args.l, 
        dataCreation_args.m,
        dataCreation_args.o
    )
    generate_data.generate_and_write_data_to_file()


if __name__ == "__main__":
    main()

# python3 random_data_generation.py -k keyFile.txt -n 50 -d 3 -l 4 -m 5 -o outputFile.txt
