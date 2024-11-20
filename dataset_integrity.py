from azure_connection import get_azure_connection
import os
import csv

def check_dataset_integrity (container_client, local_directory):
    # Elenca i file nella directory locale
    local_files = set()
    for root, dirs, files in os.walk(local_directory):
        for file in files:
            path=os.path.join(local_directory.split('/')[1],os.path.relpath(os.path.join(root, file), local_directory))
            local_files.add(path.replace("\\", "/"))

    # Elenca i file nel contenitore remoto
    remote_files = set()
    for blob in container_client.list_blobs():
        if blob.name.split('/')[0] == os.path.basename(local_directory):
            if blob.name.endswith('.gz') or blob.name.endswith('.json') or blob.name.endswith('.bval') or blob.name.endswith('.bvec') or blob.name.endswith('.tsv') or blob.name.endswith('.md') or blob.name.endswith('CHANGES') or blob.name.endswith('README') or blob.name.endswith('.eeg') or blob.name.endswith('.vhdr') or blob.name.endswith('.txt') or blob.name.endswith('.vmrk') or blob.name.endswith('.sfp') :
                remote_files.add(blob.name)


    # Confronta i file locali e remoti
    common_files = local_files.intersection(remote_files)
    only_in_local = local_files - remote_files
    only_in_remote = remote_files - local_files

    # Salva i risultati in un file CSV
    filename = os.path.basename(local_directory) + "_integrity_check.csv"
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["File", "Location"])
        
        for file in common_files:
            writer.writerow([file, "Both"])
        
        for file in only_in_local:
            writer.writerow([file, "Local"])
        
        for file in only_in_remote:
            writer.writerow([file, "Remote"])


container_client = get_azure_connection()

local_directory = input("Enter the dataset path (with /): ")
check_dataset_integrity(container_client, local_directory)
