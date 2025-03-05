import pandas as pd
import matplotlib.pyplot as plt

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


if __name__ == "__main__":
    dataset_name = input("Insert the name of the dataset: ")
    csv_path = input("Insert the path of the CSV file: ")
    plot_file_modifications(csv_path=csv_path, dataset_name=dataset_name)
