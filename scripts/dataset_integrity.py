from azure_connection import get_azure_connection
import os
import csv
import re

def check_dataset_integrity (container_client, local_directory):
    # List files of local directory
    local_files = set()
    for root, _, files in os.walk(local_directory):
        for file in files:
            path=os.path.join(local_directory.split('/')[1],os.path.relpath(os.path.join(root, file), local_directory))
            local_files.add(path.replace("\\", "/"))

    # List files of remote directory
    remote_files = set()
    pattern=r".*\.[a-zA-Z0-9]+$"
    for blob in container_client.list_blobs():
        if blob.name.split('/')[0] == os.path.basename(local_directory):
            if re.match(pattern,blob.name) or blob.name.endswith('CHANGES') or blob.name.endswith('README') or blob.name.endswith('LICENSE') or blob.name.endswith('RECORDS') or blob.name.endswith('SHA256SUMS'):
                remote_files.add(blob.name)


    # Check integrity
    common_files = local_files.intersection(remote_files)
    only_in_local = local_files - remote_files
    only_in_remote = remote_files - local_files

    filename = os.path.basename(local_directory) + "/integrity_check.csv"
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["File", "Location"])
        
        for file in common_files:
            writer.writerow([file, "Both"])
        
        for file in only_in_local:
            writer.writerow([file, "Local"])
        
        for file in only_in_remote:
            writer.writerow([file, "Remote"])


if __name__ == "__main__":
    container_name = input("Enter the container name: ")
    connection_string = input("Enter the connection string: ") 
    container_client = get_azure_connection(container_name=container_name, connection_string=connection_string)

    local_directory = input("Enter the dataset path (with /): ")
    check_dataset_integrity(container_client=container_client, local_directory=local_directory)
