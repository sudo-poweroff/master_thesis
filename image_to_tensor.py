import torch
from torchvision import transforms
from PIL import Image
from azure_connection import get_azure_connection
import os
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

def obtain_data(file_path, container_client):  
    blob_client = container_client.get_blob_client(file_path)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as temp_file:
        temp_file.write(blob_client.download_blob().readall())

def get_participant_images(blob_prefix, container_client):
    images_path = []
    blob_list = container_client.list_blobs(name_starts_with=blob_prefix)
    for blob in blob_list:
        if blob.name.endswith('.png'):
            images_path.append(blob.name)
            obtain_data(blob.name, container_client)
    return images_path

def process_participant(record, dataset, source_container_client, destination_container_client, transform):
    print(f"Processing {record['path']}...")
    participant_id = record['path']
    
    if dataset == "ecg_dataset":
        blob_prefix = f"{dataset}/files/p{str(participant_id).zfill(4)[:4]}/p{participant_id}/s{record['study_id']}/"
        images_path = get_participant_images(blob_prefix, source_container_client)
    else:
        blob_prefix = f"{dataset}/derivatives/lesion_masks/{participant_id}/"
        images_path = get_participant_images(blob_prefix, source_container_client)
        blob_prefix = f"{dataset}/{participant_id}/"
        images_path += get_participant_images(blob_prefix, source_container_client)
    
    for image_path in images_path:
        try:
            image = Image.open(image_path)

            # Apply the transformation
            image_tensor = transform(image)
            tensor_path = image_path.replace('.png', '.pt')
            if dataset == "ecg_dataset":
                tensor_path = tensor_path.replace('files/', '')
                os.makedirs(os.path.dirname(tensor_path), exist_ok=True)
            torch.save(image_tensor, tensor_path)
            
            destination_blob_client = destination_container_client.get_blob_client(blob=tensor_path)
            with open(tensor_path, "rb") as embedding:
                destination_blob_client.upload_blob(embedding, overwrite=True)
            print(f"Tensor images for participant {participant_id} uploaded to destination container!")
            os.remove(tensor_path)
            os.remove(image_path)
        except Exception as e:
            print(f"Error processing image {image_path}: {e}")
    

if __name__ == "__main__":
    source_container_name = input("Insert the source container name: ")
    destination_container_name = input("Insert the destination container name: ")
    connection_string = input("Insert the connection string: ")
    source_container_client = get_azure_connection(source_container_name, connection_string)
    destination_container_client = get_azure_connection(destination_container_name, connection_string)
    dataset = input("Insert the dataset name on which apply image-to-tensor transformation: ")

    device = "cuda" if torch.cuda.is_available() else "mps" if torch.has_mps or torch.backends.mps.is_available() else "cpu"
    print("Using device:", device)
    device = torch.device(device)

    transform = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.ToTensor()
    ])

    if dataset == "ecg_dataset":
        source_file_path = f"{dataset}/machine_measurements.csv"
    else:
        source_file_path = f"{dataset}/participants.csv"
    obtain_data(source_file_path, source_container_client) 
    
    data = pd.read_csv(source_file_path)

    # Use ThreadPoolExecutor to process multiple participants concurrently
    with ThreadPoolExecutor(max_workers=48) as executor:
        futures = [
            executor.submit(
                process_participant, 
                record, dataset, source_container_client, destination_container_client, transform
            )
            for _, record in data.iterrows()
        ]
        for future in futures:
            future.result()
    
    os.remove(source_file_path)
