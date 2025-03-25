from azure_connection import get_azure_connection
import csv
import re

def analyze_container(container_client):
    blobs = container_client.list_blobs()

    count = 0
    total_size = 0
    pattern=r".*\.[a-zA-Z0-9]+$"
    for blob in blobs:
        if re.match(pattern,blob.name) or blob.name.endswith('CHANGES') or blob.name.endswith('README') or blob.name.endswith('LICENSE') or blob.name.endswith('RECORDS') or blob.name.endswith('SHA256SUMS'):
            count += 1
            total_size += blob.size

    total_size = total_size / (1024 ** 3)
    return count, total_size


if __name__ == "__main__":
    container_name = input("Insert the container name: ")
    connection_string = input("Insert the connection string: ")
    container_client = get_azure_connection(container_name, connection_string)
    count, total_size = analyze_container(container_client)
    print(f"Total blobs in the container: {count}")
    print(f"Total size of the container: {total_size} GB")
    with open(f"containers_metrics/{container_name}_metrics.csv", "w", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Total blobs in the container", count])
        writer.writerow(["Total size of the container (GB)", total_size])