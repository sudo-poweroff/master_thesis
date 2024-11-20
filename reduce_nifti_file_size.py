import nibabel as nib
import numpy as np
import os
import csv

def analyze_nifti(file_path):
    # Load NIfTI file
    img = nib.load(file_path)
    data = img.get_fdata()
    header = img.header

    # Extract informations
    info = {
        "shape": data.shape,
        "dtype": data.dtype,
        "voxel_size": header.get_zooms(),
        "total_voxels": data.size,
        "file_size_MB": os.path.getsize(file_path) / (1024 * 1024),
    }
    return info

def nifti_4d_to_3d(input_file, output_file, method="mean"):
    # Load NiFTI file
    img = nib.load(input_file)
    data = img.get_fdata()
    
    # Check if the file is 4D
    if len(data.shape) != 4:
        print("The current file is not 4D. No changes will be made.")
        return
    
    # Reduce the 4D file to 3D
    if method == "mean":
        data_3d = np.mean(data, axis=3)  # Mean along the fourth dimension
    elif method == "max":
        data_3d = np.max(data, axis=3)  # Max along the fourth dimension
    elif method.startswith("index:"):
        index = int(method.split(":")[1])
        data_3d = data[:, :, :, index]  # Specific index along the fourth dimension
    else:
        raise ValueError("Method not recognized. Use 'mean', 'max' or 'index:<index>'")
    
    # Create a new NiFTI 3D file
    new_img = nib.Nifti1Image(data_3d, img.affine, img.header)
    
    # Save the new NiFTI file
    nib.save(new_img, output_file)
    print(f"3D file saved as: {output_file}")


def execute_reduction(file_name, dataset_path):
    with open(file_name, mode='w', newline='') as csv_file:
        fieldnames = ['file_name', 'initial_shape', 'initial_dtype', 'initial_voxel_size', 'initial_total_voxels', 'initial_file_size_MB', 'final_shape', 'final_dtype', 'final_voxel_size', 'final_total_voxels', 'final_file_size_MB']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for root, dirs, files in os.walk(dataset_path):
            for file in files:
                path = os.path.join(root, file)
                print(path)
                # if the file has a .nii.gz or .nii extension then print file info
                if path.endswith('.nii.gz') or path.endswith('.nii'):
                    initial_info = analyze_nifti(path)
                    print("File info before processing:")
                    for key, value in initial_info.items():
                        print(f"{key}: {value}")

                    nifti_4d_to_3d(path, path, method="mean")

                    final_info = analyze_nifti(path)
                    print("File info after processing:")
                    for key, value in final_info.items():
                        print(f"{key}: {value}")

                    # Write the info to the CSV file
                    writer.writerow({
                        'file_name': path,
                        'initial_shape': initial_info['shape'],
                        'initial_dtype': initial_info['dtype'],
                        'initial_voxel_size': initial_info['voxel_size'],
                        'initial_total_voxels': initial_info['total_voxels'],
                        'initial_file_size_MB': initial_info['file_size_MB'],
                        'final_shape': final_info['shape'],
                        'final_dtype': final_info['dtype'],
                        'final_voxel_size': final_info['voxel_size'],
                        'final_total_voxels': final_info['total_voxels'],
                        'final_file_size_MB': final_info['file_size_MB']
                    })


dataset_path = input("Insert the dataset path: ")
file_name = input("Insert the file name (.csv): ")
execute_reduction(file_name, dataset_path)