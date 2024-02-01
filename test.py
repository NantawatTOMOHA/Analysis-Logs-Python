import multiprocessing
from queue import Queue

def Analyze( data_queue):
    while True:
            if client.ping():
                    index_name = "switch"
                    search_query = {
                        "query": {
                            "match_all": {}
                        },
                        "size": 10
                        
                    
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
                    data_queue.put(message) 
            # Alert_email(entry['@timestamp'], entry['hostname'], entry['module_name'], entry['Brief'], entry['severity'], entry['description'])
            # insert data to table
            # Insert_data(API_INDEXNAME, entry)

def SendToEmail(data_queue):
    to_email = ['63010584@kmitl.ac.th', '63010629@kmitl.ac.th', "63010519@kmitl.ac.th"]
    while True:
        try:
            data = data_queue.get(timeout=1)  # Wait for 1 second
            EmailSender = EmailSender(USERID, USERPASS)
            EmailSender.send_email(to_email, data)
        except queue.Empty:
            # Handle the case when the queue is empty
            pass

if __name__ == "__main__":
    # ... (your setup code)

    # Sample data, replace it with your actual data or retrieval logic
    query_data = "Sample query data"

    data_queue = multiprocessing.Queue()

    Analyze_process = multiprocessing.Process(target=Analyze, args=(data_queue))
    Email_process = multiprocessing.Process(target=SendToEmail, args=(data_queue,))

    Analyze_process.start()
    Email_process.start()

    Analyze_process.join()
    Email_process.join()