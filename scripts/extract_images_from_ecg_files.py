import wfdb
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt
from azure_connection import get_azure_connection
import os
import shutil
from concurrent.futures import ThreadPoolExecutor


def bandpass_filter(signal, lowcut, highcut, fs, order=5):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return filtfilt(b, a, signal)

def extract_images_from_ecg_file(file_name, save_path):
    # Load the ECG record
    record = wfdb.rdrecord(file_name)

    signals = record.p_signal  # ECG signals
    fs = record.fs  # Sampling rate
    channels = record.sig_name  # Available channels
    os.makedirs(save_path, exist_ok=True)
    for i in range(record.n_sig):
        # Apply bandpass filter to the signal
        filtered_signal = bandpass_filter(signals[:, i], lowcut=0.5, highcut=50, fs=fs)
        path = save_path+'/'+file_name +'_'+channels[i]+ '.png'
        plt.figure(figsize=(12, 6))
        plt.plot(filtered_signal)
        plt.savefig(path)
        plt.close()

def process_blob(blob, source_container_client, destination_container_client):
    if blob.name.endswith('.dat'):
        try:
            print("Extracting images from: ", blob.name)
            directory_path = os.path.dirname(blob.name)
            if destination_container_client.get_blob_client(directory_path).exists():
                print("Images already extracted for: ", blob.name)
                return
            file_name_1 = blob.name.split('/')[-1]
            source_blob_client = source_container_client.get_blob_client(blob.name)
            with open(file_name_1, "wb") as temp_file:
                temp_file.write(source_blob_client.download_blob().readall())

            # Retrieve the other file (.hea) to extract the images 
            second_file_path = blob.name.replace('.dat', '.hea')
            file_name_2 = second_file_path.split('/')[-1]
            blob_client = source_container_client.get_blob_client(second_file_path)
            with open(file_name_2, "wb") as temp_file:
                temp_file.write(blob_client.download_blob().readall())
            
            extract_images_from_ecg_file(file_name_1.replace('.dat', ''), os.path.dirname(blob.name))
            print("Image extraction completed for: ", file_name_1)
            # Remove temporary files
            os.remove(file_name_1)
            os.remove(file_name_2)

            print("Uploading images to destination container...")
            for root, _, files in os.walk(os.path.dirname(blob.name)):
                for file in files:
                    path = os.path.join(root, file)
                    with open(path, "rb") as data:
                        destination_blob_client = destination_container_client.get_blob_client(path)
                        destination_blob_client.upload_blob(data, overwrite=True)
            print("Images uploaded to destination container!")
            folder_to_remove = os.path.join(os.path.dirname(os.path.dirname(blob.name)), os.path.basename(os.path.dirname(blob.name)))
            shutil.rmtree(folder_to_remove)
        except Exception as e:
            print(f"Error processing blob: {blob.name}: {e}")

if __name__ == "__main__":
    source_container_name = input("Enter the source container name: ")
    destination_container_name = input("Enter the destination container name: ")
    connection_string = input("Enter the connection string: ")
    source_container_client = get_azure_connection(container_name=source_container_name, connection_string=connection_string)
    destination_container_client = get_azure_connection(container_name=destination_container_name, connection_string=connection_string)

    dataset= input("Enter the dataset name for the image extraction: ")
    blob_list = source_container_client.list_blobs(name_starts_with=dataset)
    with ThreadPoolExecutor(max_workers=32) as executor:
        for blob in blob_list:
            executor.submit(process_blob, blob, source_container_client, destination_container_client)

