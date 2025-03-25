from azure.storage.blob import BlobServiceClient

def get_azure_connection (container_name,connection_string):
    account_name = "thesislakehouse"
    container_name = container_name
    connection_string = connection_string
    
    print("Connection to Azure "+container_name+" container...")
    # Create BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    # Create ContainerClient
    container_client = blob_service_client.get_container_client(container_name)
    print("Connection established!")
    return container_client

