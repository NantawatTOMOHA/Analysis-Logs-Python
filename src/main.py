import os
import smtplib
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
memory_cash=[]

# def Alert_insert_list(time,hostname,module_name,Brief,severity,description):
#     message = (
#                     str(data[0]['@timestamp']) + ', ' +
#                     str(data[0]['hostname']) + ', ' +
#                     str(data[0]['module_name']) + ', ' +
#                     str(data[0]['Brief']) + ', ' +
#                     str(data[0]['severity']) + ', ' +
#                     str(data[0]['description'])
#                     ) 
#     to_email= ['63010584@kmitl.ac.th','63010629@kmitl.ac.th',"63010519@kmitl.ac.th"]
#     samedata.append(message)
#     EmailSender = EmailSender(USERID,USERPASS)
#     EmailSender.send_email(to_email,message)
#     return True
# def Insert_data(index_name,data):
#     client.index(index=index_name, body=data)
#     return True

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
    print(file_last_modified)
    print(current_date)
    if current_date > file_last_modified:
        with open(file_path, 'w') as file:
            file.write('')

def Analyze( data_queue):
    while True:
            if client.ping():
                    index_name = "switch-2024.02.01"
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
                    'severity': '-2',  # source['severity'],
                    'description': source['description']
                }
                if int(entry['severity']) <= 4:
                    # email alert
                    message = (
                        str(entry['@timestamp']) + ', ' +
                        str(entry['hostname']) + ', ' +
                        str(entry['module_name']) + ', ' +
                        str(entry['Brief']) + ', ' +
                        str(entry['severity']) + ', ' +
                        str(entry['description'])
                    )
                    temp_timestamp=str(entry['@timestamp'])
                    
                    if not temp_timestamp in read_timestamp_from_file('./timestamps.txt'):
                        data_queue.put(message)
                        write_timestamp_to_file(temp_timestamp, './timestamps.txt')
                    clear_file('./timestamps.txt')
            # Alert_email(entry['@timestamp'], entry['hostname'], entry['module_name'], entry['Brief'], entry['severity'], entry['description'])
            # insert data to table
            # Insert_data(API_INDEXNAME, entry)

def SendToEmail(data_queue):
    to_email = ['63010584@kmitl.ac.th', '63010629@kmitl.ac.th', "63010519@kmitl.ac.th"]
    i=0;
    while True:
        try:
            data = data_queue.get(timeout=1)
            # print(type(data))
            EmailSend = EmailSender(USERID,USERPASS)
            EmailSend.send_email(to_email, data)
            
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
