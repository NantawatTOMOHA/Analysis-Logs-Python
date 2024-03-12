import os
from datetime import datetime, timedelta

class FileHandler:
    # cache module_name and description -> check duplicate send email 
    def write_to_cache(self, description, hostname, file_path):
        with open(file_path, 'a') as file:
            file.write(f"{description}::{hostname}\n")

    def read_cache_from_file(self, file_path):
        try:
            with open(file_path, 'r') as file:
                return {tuple(line.strip().split('::')) for line in file}
        except FileNotFoundError:
            return set()

    # cache timestamp -> check duplicate query data
    def write_timestamp_to_file(self, timestamp, file_path):
        with open(file_path, 'a') as file:
            file.write(timestamp + '\n')

    def read_timestamp_from_file(self, file_path):
        try:
            with open(file_path, 'r') as file:
                return [line.strip() for line in file]
        except FileNotFoundError:
            return []

    # clear data file 
    def clear_file(self,file_path, condition):
        lines_to_keep = []
        with open(file_path, 'r') as file:
            lines = file.readlines()
        if condition == False:
            lines_to_keep = lines[-50:]

        with open(file_path, 'w') as file:
            file.writelines(lines_to_keep)
