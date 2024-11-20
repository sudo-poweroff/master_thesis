from azure.storage.blob import BlobServiceClient
import os
import csv

def get_azure_connection ():
    # Configura la connessione
    account_name = "thesislakehouse"
    container_name = "rawdata"
    #Azure connection string
    connection_string = ""
    
    
    print("Connection to Azure...")
    # Crea il BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Crea un ContainerClient
    container_client = blob_service_client.get_container_client(container_name)
    print("Connection established!")
    return container_client

