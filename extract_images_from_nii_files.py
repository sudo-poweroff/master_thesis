import nibabel as nib
import numpy as np
from PIL import Image
import os
import shutil
from azure_connection import get_azure_connection

def extract_images_from_nifti_file(scanFilePath):
    #Load the scan and extract data using nibabel 
    scan = nib.load(scanFilePath)
    scanArray = scan.get_fdata()

    #Get and print the scan's shape 
    scanArrayShape = scanArray.shape
    print('The scan data array has the shape: ', scanArrayShape)

    #Examine scan's shape and header 
    scanHeader = scan.header
    print('The scan header is as follows: \n', scanHeader)

    #Calculate proper aspect ratios
    pixDim = scanHeader['pixdim'][1:4]
    aspectRatios = [pixDim[1]/pixDim[2],pixDim[0]/pixDim[2],pixDim[0]/pixDim[1]]
    print('The required aspect ratios are: ', aspectRatios)

    #Calculate new image dimensions from aspect ratio
    newScanDims = np.multiply(scanArrayShape[:3], pixDim)
    newScanDims = (round(newScanDims[0]),round(newScanDims[1]),round(newScanDims[2]))
    print('The new scan dimensions are: ', newScanDims)

    #Obtain the rotation angles
    rotation_angles=calculate_rotation_angle(scanHeader['qoffset_x'],scanHeader['qoffset_y'],scanHeader['qoffset_z'])

    outputArray = list()
    #Middle slice on 0th dimension
    slice_array = scanArray[scanArrayShape[0] // 2, :, :]
    slice_array_normalized = 255 * (slice_array - np.min(slice_array)) / (np.max(slice_array) - np.min(slice_array))
    slice_array_normalized = slice_array_normalized.astype(np.uint8)
    outputArray.append(Image.fromarray(slice_array_normalized).resize((newScanDims[2],newScanDims[1])).rotate(rotation_angles[0]))

    #Middle slice on 1st dimension
    slice_array = scanArray[:, scanArrayShape[1] // 2, :]
    slice_array_normalized = 255 * (slice_array - np.min(slice_array)) / (np.max(slice_array) - np.min(slice_array))
    slice_array_normalized = slice_array_normalized.astype(np.uint8)
    outputArray.append(Image.fromarray(slice_array_normalized).resize((newScanDims[2],newScanDims[0])).rotate(rotation_angles[1]))

    #Middle slice on 2nd dimension
    slice_array = scanArray[:, :, scanArrayShape[2] // 2]
    slice_array_normalized = 255 * (slice_array - np.min(slice_array)) / (np.max(slice_array) - np.min(slice_array))
    slice_array_normalized = slice_array_normalized.astype(np.uint8)
    if rotation_angles[2]=='lr-90':
        image = Image.fromarray(slice_array_normalized).resize((newScanDims[1],newScanDims[0])).transpose(Image.FLIP_LEFT_RIGHT)
        outputArray.append(image.rotate(-90))
    else:
        outputArray.append(Image.fromarray(slice_array_normalized).resize((newScanDims[1],newScanDims[0])).rotate(rotation_angles[2]))

    return outputArray

def calculate_rotation_angle(qoffset_x,qoffset_y,qoffset_z):
    if qoffset_x<0 and qoffset_y<0 and qoffset_z<0:
        return 90,90,90
    elif qoffset_x>0 and qoffset_y<0 and qoffset_z<0:
        return 90,90,90
    elif qoffset_x>0 and qoffset_y>0 and qoffset_z<0:
        return 180,-90,90
    elif qoffset_x<0 and qoffset_y>0 and qoffset_z<0:
        return 180,0,'lr-90'
    elif qoffset_x<0 and qoffset_y<0 and qoffset_z>0:
        return 90,90,90
    elif qoffset_x<0 and qoffset_y>0 and qoffset_z>0:
        return 180,0,'lr-90'
    elif qoffset_x>0 and qoffset_y<0 and qoffset_z>0:
        return 90,90,90
    elif qoffset_x>0 and qoffset_y>0 and qoffset_z>0:
        return 180,0,'lr-90'
    elif qoffset_x==0 and qoffset_y==0 and qoffset_z==0:
        return 90,90,90
    else:
        return 0,0,0

if __name__ == "__main__":
    source_container_name = input("Enter the source container name: ")
    destination_container_name = input("Enter the destination container name: ")
    connection_string = input("Enter the connection string: ")
    source_container_client = get_azure_connection(container_name=source_container_name, connection_string=connection_string)
    destination_container_client = get_azure_connection(container_name=destination_container_name, connection_string=connection_string)
    dataset= input("Enter the dataset name for the image extraction: ")
    blob_list = source_container_client.list_blobs(name_starts_with=dataset)
    
    for blob in blob_list:
        source_blob_client = source_container_client.get_blob_client(blob.name)
        if blob.name.endswith('.nii.gz') or blob.name.endswith('.nii'):
            print("Extracting images from: ", blob.name)
            file_name = blob.name.split('/')[-1]
            with open(file_name, "wb") as temp_file:
                temp_file.write(source_blob_client.download_blob().readall())
            slices = extract_images_from_nifti_file(file_name)
            
            print("Image extraction completed for: ", file_name)
            os.remove(file_name)
            print("Uploading images to destination container...")
            i=0
            for slice in slices: 
                destination_path=blob.name.split('.')[0]+'_dim'+str(i)+'_middle_slice.png'
                os.makedirs(os.path.dirname(destination_path), exist_ok=True)
                slice.save(destination_path)
                destination_blob_client = destination_container_client.get_blob_client(blob=destination_path)
                with open(destination_path, "rb") as data:
                    destination_blob_client.upload_blob(data, overwrite=True)
                i+=1
            print("Images uploaded to destination container!")
            shutil.rmtree(os.path.join(destination_path.split('/')[0],destination_path.split('/')[1]))