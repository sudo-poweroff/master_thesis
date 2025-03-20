import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def plot_file_modifications(csv_path, dataset_name):
    df = pd.read_csv(csv_path)
    
    total_files = len(df)
    modified_files = len(df[df["initial_shape"] != df["final_shape"]])
    
    plt.figure(figsize=(6, 4))
    plt.bar(["Total", "Modified"], [total_files, modified_files], color=['blue', 'orange'])
    plt.xlabel("Category")
    plt.ylabel("Number of files")
    plt.title(f"Modified files vs total - {dataset_name.capitalize()} Dataset")
    plt.ylim(0, max(total_files, modified_files) * 1.1)
    plt.savefig(f"plots/{dataset_name}_file_modifications.png")
    plt.show()

def plot_datasets_dimension():
    datasets = ["Alzheimer", "Aphasia", "Stroke"]
    initial_dimensions = [240.19, 272.85, 272.85]
    final_dimensions = [0.577, 8.78, 272.85]

    _, ax = plt.subplots(figsize=(8, 6))
    bar_width = 0.4
    indices = np.arange(len(datasets))

    bars1 = ax.bar(indices - bar_width/2, initial_dimensions, bar_width, label="Initial dimension (GB)", color="blue")
    bars2 = ax.bar(indices + bar_width/2, final_dimensions, bar_width, label="Final dimension (GB)", color="orange")

    ax.set_xlabel("Dataset")
    ax.set_ylabel("Dimension (GB)")
    ax.set_title("MRI datasets dimension after 4D -> 3D conversion")
    ax.set_xticks(indices)
    ax.set_xticklabels(datasets)
    ax.legend()

    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.annotate(f"{height:.2f} GB", 
                        xy=(bar.get_x() + bar.get_width() / 2, height), 
                        xytext=(0, 3),  
                        textcoords="offset points", 
                        ha="center", va="bottom")
    plt.savefig("plots/datasets_dimension.png")
    plt.show()


def plot_container_dimension():
    containers = ["rawdata", "processeddata", "standardizeddata", "aireadydata"]
    num_files = [333912, 1850678, 32458, 2154405]
    dimensioni_gb = [93.4546172330156, 112.09717944450676, 3.276502446271479, 1776.0435373485088]

    indices = np.arange(len(containers))

    _, ax1 = plt.subplots(figsize=(8, 5))
    ax1.bar(indices, num_files, color="blue")
    ax1.set_xlabel("Container")
    ax1.set_ylabel("Number of Files")
    ax1.set_title("Number of Files in Each Container")
    ax1.set_xticks(indices)
    ax1.set_xticklabels(containers)

    for i, v in enumerate(num_files):
        ax1.text(i, v + max(num_files) * 0.02, str(v), ha='center', fontsize=10)

    plt.savefig("plots/containers_files.png")
    plt.show()

    _, ax2 = plt.subplots(figsize=(8, 5))
    ax2.bar(indices, dimensioni_gb, color="orange")
    ax2.set_xlabel("Container")
    ax2.set_ylabel("Dimension (GB)")
    ax2.set_title("Container Dimensions in GB")
    ax2.set_xticks(indices)
    ax2.set_xticklabels(containers)

    for i, v in enumerate(dimensioni_gb):
        ax2.text(i, v + max(dimensioni_gb) * 0.02, f"{v:.2f}", ha='center', fontsize=10)

    plt.savefig("plots/containers_dimension.png")
    plt.show()



if __name__ == "__main__":
    #dataset_name = input("Insert the name of the dataset: ")
    #csv_path = input("Insert the path of the CSV file: ")
    #plot_file_modifications(csv_path=csv_path, dataset_name=dataset_name)
    
    #plot_datasets_dimension()
    plot_container_dimension()