import os
from dotenv import load_dotenv
from elasticsearch import Elasticsearch

load_dotenv('../.env')
URL=os.getenv('URL')
CA_CERT=os.getenv('CA_CERT')
API_ID=os.getenv('API_ID')
API_KEY=os.getenv('API_KEY')

client = Elasticsearch(
    URL,
    ca_certs=CA_CERT,
    api_key=(API_ID, API_KEY) 
)

print(client.ping())

# if client.ping():
#     # Define your index and type (if applicable)
#     index_name = "your_index_name"
#     document_type = "your_document_type"  # Set to None if you're using Elasticsearch 7.x or later

#     # Example search query (match_all)
#     search_query = {
#         "query": {
#             "match_all": {}
#         }

    
#     }
#     search_results = client.search(index=index_name, doc_type=document_type, body=search_query)

# else:
#     print("Failed to connect")

# {'name': 'instance-0000000000', 'cluster_name': ...}
# client.info()