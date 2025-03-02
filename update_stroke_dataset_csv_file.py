import pandas as pd
from azure_connection import get_azure_connection
import os
import shutil

def add_missing_rows(file_path):
    data = pd.read_csv(file_path, sep='\t', na_values='n/a')
    blob_list = source_container_client.list_blobs(name_starts_with='stroke_dataset/sub-')
    for blob in blob_list:
        subject = blob.name.split('/')[1]
        if subject not in data['participant_id'].values:
            print(f"{subject} is not present in the CSV file. Adding {subject} to the CSV file.")
            new_row = {'participant_id': subject}
            data = pd.concat([data, pd.DataFrame([new_row], columns=data.columns)])

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

    blob_client = source_container_client.get_blob_client('stroke_dataset/participants.tsv')
    file_path = 'stroke_dataset/participants.csv'
    os.makedirs(os.path.dirname(file_path), exist_ok=True)  
    with open(file_path, "wb") as temp_file:
        temp_file.write(blob_client.download_blob().readall())

    add_missing_rows(file_path=file_path)
    os.remove(file_path)

    
