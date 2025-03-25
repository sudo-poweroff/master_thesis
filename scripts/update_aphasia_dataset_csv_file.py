import pandas as pd
from azure_connection import get_azure_connection
import os

def remove_rows(file_path):
    data = pd.read_csv(file_path, sep='\t', na_values='n/a')
    new_data = data.head(0)
    blob_list = source_container_client.list_blobs(name_starts_with='aphasia_dataset/sub-M')
    for blob in blob_list:
        subject = blob.name.split('/')[1]
        if subject in data['participant_id'].values and subject not in new_data['participant_id'].values:
            new_row = data[data['participant_id']==subject]
            new_data = pd.concat([new_data, new_row])
        elif subject not in data['participant_id'].values:
            print(f"{subject} is not present in the CSV file.")

    new_data.to_csv(file_path, sep=',', index=False, na_rep='n/a')        

    destination_blob_client = destination_container_client.get_blob_client(blob=file_path)
    with open(file_path, "rb") as data:
        destination_blob_client.upload_blob(data, overwrite=True)
    

if __name__ == "__main__":
    source_container_name = input("Insert the source container name: ")
    destination_container_name = input("Insert the destination container name: ")
    connection_string = input("Insert the connection string: ")
    source_container_client = get_azure_connection(source_container_name, connection_string)
    destination_container_client = get_azure_connection(destination_container_name, connection_string)

    blob_client = source_container_client.get_blob_client('aphasia_dataset/participants.tsv')
    file_path = 'aphasia_dataset/participants.csv'
    os.makedirs(os.path.dirname(file_path), exist_ok=True)  
    with open(file_path, "wb") as temp_file:
        temp_file.write(blob_client.download_blob().readall())

    remove_rows(file_path=file_path)
    os.remove(file_path)

