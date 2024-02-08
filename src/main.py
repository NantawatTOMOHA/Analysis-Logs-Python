import os
from emailsender import EmailSender
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from multiprocessing import Process, Queue
import queue
from datetime import datetime

load_dotenv('../.env')
URL=os.getenv('URL')
CA_CERT=os.getenv('CA_CERT')
API_ID=os.getenv('API_ID')
API_KEY=os.getenv('API_KEY')
API_INDEXNAME=os.getenv('API_INDEXNAME')
USERID=os.getenv("USERID")
USERPASS=os.getenv("USERPASS")

client = Elasticsearch(
    URL,
    ca_certs=CA_CERT,
    api_key=(API_ID, API_KEY) 
)

severity_level_map = {
    0: "Emergency (Emergency condition)",
    1: "Alert (Errors needing immediate actions)",
    2: "Critical (Critical condition)",
}

def write_timestamp_to_file(timestamp, file_path):
    with open(file_path, 'a') as file:
        file.write(timestamp + '\n')

def read_timestamp_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return [line.strip() for line in file]
    except FileNotFoundError:
        return []
    
def clear_file(file_path):

    current_date = datetime.now().date()
    file_last_modified = datetime.fromtimestamp(os.path.getmtime(file_path)).date()

    if current_date > file_last_modified:
        with open(file_path, 'r') as file:
            lines = file.readlines()

        lines_to_keep = lines[-50:]

        with open(file_path, 'w') as file:
            file.writelines(lines_to_keep)
    
def Create_alert_Index(index_name_alert,data):
    try:
        if not client.indices.exists(index=index_name_alert):
            client.indices.create(index=index_name_alert)
            print(f"Index created: {index_name_alert}")
        else: 
            client.index(index=index_name_alert,body=data)
            print(f"Push new event into : {index_name_alert}")
            
    except Exception as e :
        print(f"Failed to create index: {e}")


def Analyze( data_queue):
    while True:
            if client.ping():
                    current_date = datetime.now().strftime("%Y.%m.%d")
                    index_name = f"switch-{current_date}"
                    index_name_alert = f"alert-switch-{current_date}"
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

            search_results = client.search(index=index_name,  body=search_query)
            for hit in search_results['hits']['hits']:
                source = hit['_source']
                entry = {
                    '@timestamp': source['@timestamp'],
                    'hostname': source['hostname'],
                    'module_name': source['module_name'],
                    'Brief': source['Brief'],
                    'severity':  source['severity'],
                    'description': source['description']
                }
                if int(entry['severity']) <= 2 :
                    # email alert
                    temp_timestamp=str(entry['@timestamp'])
                    
                    if not temp_timestamp in read_timestamp_from_file('./timestamps.txt'):
                        data_queue.put(entry)
                        Create_alert_Index(index_name_alert,entry)
                        write_timestamp_to_file(temp_timestamp, './timestamps.txt')
                        clear_file('./timestamps.txt')
                        
def SendToEmail(data_queue):
    to_email = ['63010584@kmitl.ac.th', '63010629@kmitl.ac.th', "63010519@kmitl.ac.th"]
    while True:
        try:
            data = data_queue.get(timeout=1)
            EmailSend = EmailSender(USERID,USERPASS)
            EmailSend.send_email(to_email, str(data['description']), str(data['module_name']) , str(data['hostname']) , str(data['@timestamp']),severity_level_map[int(data['severity'])])            
        except queue.Empty:
            pass

if __name__ == "__main__":

        data_queue = Queue()

        Analyze_process = Process(target=Analyze, args=(data_queue,))
        
        Email_process = Process(target=SendToEmail, args=(data_queue,))

        Analyze_process.start()
        Email_process.start()

        Analyze_process.join()
        Email_process.join()
