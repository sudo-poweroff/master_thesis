import torch
import pandas as pd
from azure_connection import get_azure_connection
import os
import shutil

def obtain_data(file_path):
    blob_client = container_client.get_blob_client(file_path)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)  
    with open(file_path, "wb") as temp_file:
        temp_file.write(blob_client.download_blob().readall())

if __name__ == '__main__':
    device = "cuda" if torch.cuda.is_available() else "mps" if torch.has_mps or torch.backends.mps.is_available() else "cpu"
    print("Using device:", device)
    device = torch.device(device)

    container_name = input("Insert the container name: ")
    connection_string = input("Insert the connection string: ")
    container_client = get_azure_connection(container_name, connection_string)
    dataset = input("Insert the dataset name on which apply AI data conversion: ")
    
    if 'alzheimer_dataset' in dataset:
        file_path = f'alzheimer_dataset/participants_second_phase_{dataset.split("_")[-1]}_final.csv'
        dataset = 'alzheimer_dataset'
    elif dataset == 'ecg_dataset':
        file_path = f'{dataset}/machine_measurements_final.csv'
    else:
        file_path = f'{dataset}/participants_final.csv'
    obtain_data(file_path)

    df = pd.read_csv(file_path)
    for _, row in df.iterrows():
        # Convert the row to a tensor
        participant_id = row['participant_id']
        if dataset == 'ecg_dataset':
            study_id = row['study_id']
            row = row.drop(labels=['participant_id', 'study_id', 'cart_id'])
            row['ecg_time'] = pd.to_datetime(row['ecg_time']).timestamp()
        else:
            row = row.drop(labels=['participant_id'])
        row = pd.to_numeric(row, errors='coerce')
        row_tensor = torch.tensor(row.values, dtype=torch.float32)
        if dataset == 'ecg_dataset':
            output_file_path = f"{dataset}/p{str(participant_id).zfill(4)[:4]}/p{participant_id}/s{study_id}/tabular_data.pt"
        else:
            output_file_path = f"{dataset}/{participant_id}/tabular_data.pt"
        os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
        torch.save(row_tensor, output_file_path)

        destination_blob_client = container_client.get_blob_client(blob=output_file_path)
        with open(output_file_path, "rb") as tabular_data:
            destination_blob_client.upload_blob(tabular_data, overwrite=True)
        print(f'Tensor tabular data for participant {participant_id} uploaded to destination container!')
        if dataset == 'ecg_dataset':
            shutil.rmtree(f"ecg_dataset/{output_file_path.split('/')[1]}")
        else:
            shutil.rmtree(output_file_path.replace('/tabular_data.pt', ''))

    os.remove(file_path)