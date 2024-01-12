import os
import smtplib
from dotenv import load_dotenv
from elasticsearch import Elasticsearch

load_dotenv('../.env')
URL=os.getenv('URL')
CA_CERT=os.getenv('CA_CERT')
API_ID=os.getenv('API_ID')
API_KEY=os.getenv('API_KEY')
API_INDEXNAME=os.getenv('API_INDEXNAME')
client = Elasticsearch(
    URL,
    ca_certs=CA_CERT,
    api_key=(API_ID, API_KEY) 
)


def Alert_email(time,hostname,module_name,Brief,severity,description):

    return True
def Insert_data(index_name,data):
    client.index(index=index_name, body=data)
    return True



print(client.ping())
# server = smtplib.SMTP('smtp.gmail.com',587)
# server.starttls()
# server.login('socserverproject@gmail.com','server_101_nwp_')
# server.sendmail('socserverproject@gmail.com','nantwat.385@gmail.com',"test mail")
# print('mail sent')
if client.ping():
    # Define your index and type (if applicable)
    index_name = "logstash-grok"
    # document_type = "none"  # Set to None if you're using Elasticsearch 7.x or later

    # Example search query (match_all)
    search_query = {
        "query": {
            "match_all": {}
        },
        "size": 10
        
    
    }
    search_results = client.search(index=index_name,  body=search_query)
    # print(search_results)
    # i = True
# while  i == 1 :
    data = []
    for hit in search_results['hits']['hits']:
            source = hit['_source']
            entry = {
                '@timestamp': source['@timestamp'],
                'hostname': source['hostname'],
                'module_name': source['module_name'],
                'Brief': source['Brief'],
                'severity': '-2', #source['severity'],
                'description': source['description']
                    }
            data.append(entry)
    print(data)
    print(len(data))
    for i in range(0,len(data)):
            if int(data[0]['severity'])<=4 :
                #email alert
                # Alert_email(data[0]['@timestamp'],data[0]['hostname'],data[0]['module_name'],data[0]['Brief'],data[0]['severity'],data[0]['description'])
                #insert data to table
                Insert_data(API_INDEXNAME,data[0])
                data.pop(0)
            elif data[0]['severity'] ==100  :
                print("i")
                data.pop(0)
            else : data.pop(0)

# else:
#     print("Failed to connect")

# {'name': 'instance-0000000000', 'cluster_name': ...}
# client.info()
