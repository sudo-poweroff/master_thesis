import nibabel as nib
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import os


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

    #Display scan array's middle slices
    #fig, axs = plt.subplots(1,3)
    #fig.suptitle('Scan Array (Middle Slices)')
    #axs[0].imshow(scanArray[scanArrayShape[0]//2,:,:], cmap='gray')
    #axs[1].imshow(scanArray[:,scanArrayShape[1]//2,:], cmap='gray')
    #axs[2].imshow(scanArray[:,:,scanArrayShape[2]//2], cmap='gray')
    #fig.tight_layout()
    #plt.show()

    #Calculate proper aspect ratios
    pixDim = scanHeader['pixdim'][1:4]
    aspectRatios = [pixDim[1]/pixDim[2],pixDim[0]/pixDim[2],pixDim[0]/pixDim[1]]
    print('The required aspect ratios are: ', aspectRatios)

    #Display scan array's middle slices with proper aspect ratio
    #fig, axs = plt.subplots(1,3)
    #fig.suptitle('Scan Array w/ Proper Aspect Ratio (Middle Slices)')
    #axs[0].imshow(scanArray[scanArrayShape[0]//2,:,:], aspect = aspectRatios[0], cmap='gray')
    #axs[1].imshow(scanArray[:,scanArrayShape[1]//2,:], aspect = aspectRatios[1], cmap='gray')
    #axs[2].imshow(scanArray[:,:,scanArrayShape[2]//2], aspect = aspectRatios[2], cmap='gray')
    #fig.tight_layout()
    #plt.show()

    #Calculate new image dimensions from aspect ratio
    newScanDims = np.multiply(scanArrayShape[:3], pixDim)
    newScanDims = (round(newScanDims[0]),round(newScanDims[1]),round(newScanDims[2]))
    print('The new scan dimensions are: ', newScanDims)

    #Set the output file path
    outputPath = 'C:/Users/sdell/projects/master_thesis'

    #Obtain the rotation angles
    rotation_angles=calculate_rotation_angle(scanHeader['qoffset_x'],scanHeader['qoffset_y'],scanHeader['qoffset_z'])
    if all(angle == 0 for angle in rotation_angles):
       raise ValueError("Rotation angles contain only 0, which is not allowed.")

    #Middle slice on 0th dimension
    slice_array = scanArray[scanArrayShape[0] // 2, :, :]
    slice_array_normalized = 255 * (slice_array - np.min(slice_array)) / (np.max(slice_array) - np.min(slice_array))
    slice_array_normalized = slice_array_normalized.astype(np.uint8)
    outputArray = Image.fromarray(slice_array_normalized).resize((newScanDims[2],newScanDims[1])).rotate(rotation_angles[0])
    outputArray.save(outputPath+'/Dim0_middle_Slice_gray_dwi.png')

    #Middle slice on 1st dimension
    slice_array = scanArray[:, scanArrayShape[1] // 2, :]
    slice_array_normalized = 255 * (slice_array - np.min(slice_array)) / (np.max(slice_array) - np.min(slice_array))
    slice_array_normalized = slice_array_normalized.astype(np.uint8)
    outputArray = Image.fromarray(slice_array_normalized).resize((newScanDims[2],newScanDims[0])).rotate(rotation_angles[1])
    outputArray.save(outputPath+'/Dim1_middle_Slice_gray_dwi.png')

    #Middle slice on 2nd dimension
    slice_array = scanArray[:, :, scanArrayShape[2] // 2]
    slice_array_normalized = 255 * (slice_array - np.min(slice_array)) / (np.max(slice_array) - np.min(slice_array))
    slice_array_normalized = slice_array_normalized.astype(np.uint8)
    if rotation_angles[2]=='lr-90':
        outputArray = Image.fromarray(slice_array_normalized).resize((newScanDims[1],newScanDims[0])).transpose(Image.FLIP_LEFT_RIGHT)
        outputArray = outputArray.rotate(-90)
    else:
        outputArray = Image.fromarray(slice_array_normalized).resize((newScanDims[1],newScanDims[0])).rotate(rotation_angles[2])
    outputArray.save(outputPath+'/Dim2_middle_Slice_gray_dwi.png')


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
    

##Define the filepath to your NIfTI scan
#scanFilePath = 'D:/aphasiaDataset/sub-M2001/ses-1076/anat/sub-M2001_ses-1076_acq-tfl3_run-4_T1w.nii.gz'
#extract_images_from_nifti_file(scanFilePath)
def extract_images(path):
    for root, dirs, files in os.walk(path):
            for file in files:
                path = os.path.join(root, file)
                print(path)
                # if the file has a .nii.gz or .nii extension then print file info
                if path.endswith('.nii.gz') or path.endswith('.nii'):
                    extract_images_from_nifti_file(path)

extract_images('D:/aphasiaDataset')