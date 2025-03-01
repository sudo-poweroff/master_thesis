from azure_connection import get_azure_connection
import pandas as pd
import os
import shutil


def join_report_fields(file_path):
    data = pd.read_csv(file_path)

    # Filter columns that start with "report_"
    report_columns = [col for col in data.columns if col.startswith('report_')]

    # Unify the report fields into a single column
    data['report'] = data[report_columns].apply(
        lambda row: 'The patient has ' + ', '.join(row.dropna().astype(str)), axis=1
    )

    # Remove the original report fields
    data = data.drop(columns=report_columns)

    data.to_csv(file_path, index=False)
    print("The report fields have been joined and saved to the CSV file.")





if __name__ == "__main__":
    source_container_name = input("Insert the source container name: ")
    destination_container_name = input("Insert the destination container name: ")
    connection_string = input("Insert the connection string: ")
    source_container_client = get_azure_connection(source_container_name, connection_string)
    destination_container_client = get_azure_connection(destination_container_name, connection_string)

    blob_client = source_container_client.get_blob_client('ecg_dataset/machine_measurements.csv')
    file_path = 'ecg_dataset/machine_measurements.csv'
    os.makedirs(os.path.dirname(file_path), exist_ok=True)  
    with open(file_path, "wb") as temp_file:
        temp_file.write(blob_client.download_blob().readall())
    join_report_fields(file_path = file_path)

    destination_blob_client = destination_container_client.get_blob_client(blob=file_path)
    with open(file_path, "rb") as data:
        destination_blob_client.upload_blob(data, overwrite=True)
    print("The updated CSV file has been uploaded to the destination container.")
    shutil.rmtree(file_path.split('/')[0])