from azure.storage.blob import BlobServiceClient
import os
import csv

def get_azure_connection ():
    # Configura la connessione
    account_name = "thesislakehouse"
    container_name = "rawdata"
    #Azure connection string
    connection_string = "BlobEndpoint=https://thesislakehouse.blob.core.windows.net/;QueueEndpoint=https://thesislakehouse.queue.core.windows.net/;FileEndpoint=https://thesislakehouse.file.core.windows.net/;TableEndpoint=https://thesislakehouse.table.core.windows.net/;SharedAccessSignature=sv=2022-11-02&ss=bfqt&srt=sco&sp=rwdlacupyx&se=2024-11-30T22:05:07Z&st=2024-11-18T16:05:07Z&spr=https&sig=vtkB%2BO%2BOEZmhAOuCzQUrebEL61f6KzNz5gohQwQAxms%3D"
    
    
    print("Connection to Azure...")
    # Crea il BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Crea un ContainerClient
    container_client = blob_service_client.get_container_client(container_name)
    print("Connection established!")
    return container_client

