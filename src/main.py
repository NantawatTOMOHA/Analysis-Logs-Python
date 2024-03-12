import os
import queue
import re
import sys
import time
import schedule 
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from multiprocessing import Process, Queue
from datetime import datetime, timedelta
sys.path.append("..")
from modules.emailsender import EmailSender
from modules.file_handler import FileHandler

# load env
load_dotenv('../.env')
file_handler = FileHandler()  # Create an instance of FileHandler

# getenv
URL = os.getenv('URL')
CA_CERT = os.getenv('CA_CERT')
API_ID = os.getenv('API_ID')
API_KEY = os.getenv('API_KEY')
API_INDEXNAME = os.getenv('API_INDEXNAME')
USERID = os.getenv("USERID")
USERPASS = os.getenv("USERPASS")

# connect Elasticsearch
client = Elasticsearch(
    URL,
    ca_certs=CA_CERT,
    api_key=(API_ID, API_KEY)
)

# severity level
severity_level_map = {
    0: "Emergency (Emergency condition)",
    1: "Alert (Errors needing immediate actions)",
    2: "Critical (Critical condition)",
}


# Create alert index
def Create_alert_Index(index_name_alert, data):
    try:
        if not client.indices.exists(index=index_name_alert):
            client.indices.create(index=index_name_alert)
            print(f"Index created: {index_name_alert}")
        else:
            client.index(index=index_name_alert, body=data)
            print(f"Push new event into : {index_name_alert}")

    except Exception as e:
        print(f"Failed to create index: {e}")

# Analyze function
def Analyze(data_queue):
    while True:
        if client.ping():
            current_date = (datetime.now() - timedelta(hours=7)).strftime("%Y.%m.%d")
            index_name = f"switch-{current_date}"
            index_name_alert = f"alert-switch-{current_date}"
            if not client.indices.exists(index=index_name):
                time.sleep(10)  # Adjust the sleep time as needed
                continue

            search_query = {
                "query": {
                    "match_all": {}
                },
                "size": 10,
                "sort": [
                    {
                        "@timestamp": {
                            "order": "desc"
                        }
                    }
                ]
            }

            try:
                search_results = client.search(index=index_name, body=search_query)
                for hit in search_results['hits']['hits']:
                    source = hit['_source']
                    entry = {
                        '@timestamp': source['@timestamp'],
                        'hostname': source['hostname'],
                        'module_name': source['module_name'],
                        'Brief': source['Brief'],
                        'severity': source['severity'],
                        'description': source['description']
                    }
                    if int(entry['severity']) <= 2:
                        # email alert
                        cache = file_handler.read_cache_from_file("../cache/email_cache.txt")
                        entry_tuple = (entry['description'], entry['hostname'])
                        if entry_tuple not in cache:
                            temp_timestamp = str(entry['@timestamp'])
                            if temp_timestamp not in file_handler.read_timestamp_from_file('../cache/timestamps.txt'):
                                data_queue.put(entry)
                                print("sent to alert log Dashboard:", index_name_alert)
                                Create_alert_Index(index_name_alert, entry)
                                file_handler.write_to_cache(entry['description'], entry['hostname'],"../cache/email_cache.txt")
                                file_handler.write_timestamp_to_file(temp_timestamp, '../cache/timestamps.txt')

            except Exception as e:
                print(f"Error during search: {e}")

# Send Email function
def SendToEmail(data_queue):
    while True:
        try:
            to_email = []
            with open("/home/Email_management-Python/src/list_email.txt", 'r') as file:
                for line in file:
                    stripped_line = line.strip()
                    if stripped_line:
                        to_email.append(stripped_line)
            data = data_queue.get(timeout=1)
            EmailSend = EmailSender(USERID, USERPASS)
            EmailSend.send_email(to_email, str(data['description']), str(data['module_name']), str(data['hostname']), str(data['@timestamp']), severity_level_map[int(data['severity'])])
        except queue.Empty:
            pass

# clear file every 07:00 am
def clear_files_job():
    file_handler.clear_file('../cache/email_cache.txt', True)
    file_handler.clear_file('../cache/timestamps.txt', False)

def schedule_job():
    schedule.every().day.at("07:00").do(clear_files_job)

    while True: 
        schedule.run_pending()
        time.sleep(1)
# Main
if __name__ == "__main__":

    data_queue = Queue()

    schedule_process = Process(target=schedule_job)
    Analyze_process = Process(target=Analyze, args=(data_queue,))
    Email_process = Process(target=SendToEmail, args=(data_queue,))

    schedule_process.start()
    Analyze_process.start()
    Email_process.start()

    Analyze_process.join()
    Email_process.join()
