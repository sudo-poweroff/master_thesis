from transformers import BertTokenizer, BertModel
import torch
import json
import pandas as pd
from azure_connection import get_azure_connection
import os

def obtain_data(file_path, container_client):  
    blob_client = container_client.get_blob_client(file_path)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as temp_file:
        temp_file.write(blob_client.download_blob().readall())

def tokenize_and_embed_text(source_file_path):
    with open(source_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

    for record in data:
        print(f"Processing {record['input']['participant_id']}...")
        if record["generated_text"]!= "n/a":
            # Tokenization
            input_ids = tokenizer(record["generated_text"], return_tensors="pt", padding=True, truncation=True, max_length=256)
            # Embedding extraction
            with torch.no_grad():
                outputs = model(**input_ids)

            # The embeddings are in the "last_hidden_state" key
            embedding = outputs.last_hidden_state
            # Pooling to represent the entire text
            text_embedding = torch.mean(embedding, dim=1)
          
            output_file_path = f"{dataset}/{record['input']['participant_id']}/text_embedding.pt"
            os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
            torch.save(text_embedding, output_file_path)

            destination_blob_client = destination_container_client.get_blob_client(blob=output_file_path)
            with open(output_file_path, "rb") as embedding:
                destination_blob_client.upload_blob(embedding, overwrite=True)
            print(f"Embedded text for participant {record['input']['participant_id']} uploaded to destination container!")
            os.remove(output_file_path)
        else:
            print(f"Participant {record['input']['participant_id']} has no text data, skipping...")

def tokenize_and_embed_ecg_text(source_file_path):
    data = pd.read_csv(source_file_path)
    for _, record in data.iterrows():
        print(f"Processing {record['participant_id']}-{record['study_id']}...")
        if record["report"]!= "n/a":
            # Tokenization
            input_ids = tokenizer(record["report"], return_tensors="pt", padding=True, truncation=True, max_length=128)
            # Embedding extraction
            with torch.no_grad():
                outputs = model(**input_ids)

            # The embeddings are in the "last_hidden_state" key
            embedding = outputs.last_hidden_state
            # Pooling to represent the entire text
            text_embedding = torch.mean(embedding, dim=1)
    
            output_file_path = f"{dataset}/p{str(record['participant_id']).zfill(4)[:4]}/p{record['participant_id']}/s{record['study_id']}/text_embedding.pt"
            os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
            torch.save(text_embedding, output_file_path)

            destination_blob_client = destination_container_client.get_blob_client(blob=output_file_path)
            with open(output_file_path, "rb") as embedding:
                destination_blob_client.upload_blob(embedding, overwrite=True)
            print(f"Embedded text for participant {record['participant_id']} uploaded to destination container!")
            os.remove(output_file_path)
        else:
            print(f"Participant {record['participant_id']} has no text data, skipping...")    


if __name__ == "__main__":
    source_container_name = input("Insert the source container name: ")
    destination_container_name = input("Insert the destination container name: ")
    connection_string = input("Insert the connection string: ")
    source_container_client = get_azure_connection(source_container_name, connection_string)
    destination_container_client = get_azure_connection(destination_container_name, connection_string)
    dataset = input("Insert the dataset name on witch apply text tokenization and embedding: ")

    if dataset == "ecg_dataset":
        source_file_path = f"{dataset}/machine_measurements.csv"
        function = tokenize_and_embed_ecg_text
    else:
        source_file_path = f"{dataset}/generated_text_data.json"
        function = tokenize_and_embed_text

    obtain_data(source_file_path, source_container_client)

    device = "cuda" if torch.cuda.is_available() else "mps" if torch.has_mps or torch.backends.mps.is_available() else "cpu"
    print("Using device:", device)
    device = torch.device(device)

    # Load the pre-trained BERT model and tokenizer
    tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
    model = BertModel.from_pretrained("bert-base-uncased")
    
    function(source_file_path)
    os.remove(source_file_path)