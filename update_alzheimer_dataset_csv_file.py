from azure_connection import get_azure_connection
import os
import pandas as pd

def update_csv_file(file_path):
    data = pd.read_csv(file_path, sep='\t', na_values='n/a')
    data = data.map(lambda x: str(int(x)) if isinstance(x, float) and x.is_integer() else x)

    data.to_csv(file_path, sep=',', index=False, na_rep='n/a')

    destination_blob_client = destination_container_client.get_blob_client(blob=file_path)
    with open(file_path, "rb") as data:
        destination_blob_client.upload_blob(data, overwrite=True)


    
if __name__ == "__main__":
    source_container_name = input("Insert the source container name: ")
    destination_container_name = input("Insert the destination container name: ")
    connection_string = input("Insert the connection string: ")
    source_container_client = get_azure_connection(source_container_name, connection_string)
    destination_container_client = get_azure_connection(destination_container_name, connection_string)

    blob_client = source_container_client.get_blob_client('alzheimer_dataset/participants.tsv')
    file_path = 'alzheimer_dataset/participants.csv'
    os.makedirs(os.path.dirname(file_path), exist_ok=True)  
    with open(file_path, "wb") as temp_file:
        temp_file.write(blob_client.download_blob().readall())

    update_csv_file(file_path=file_path)
    os.remove(file_path)