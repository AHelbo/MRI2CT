import numpy as np
import glob
import os
import nibabel 
import tifffile
from config import INPUT_DIR, BAD_DATA, EXCLUDE_BAD_DATA, GLOBAL_CT_MAX, GLOBAL_CT_MIN
from src.utils import read_list_from_file, print_hierarchical


def make_square(image):
    # Get the current dimensions of the image
    rows, cols = image.shape

    # Determine the size of the square (largest dimension)
    size = max(rows, cols)

    # Calculate padding for rows
    pad_rows = (size - rows) // 2
    pad_rows_extra = (size - rows) % 2

    # Calculate padding for columns
    pad_cols = (size - cols) // 2
    pad_cols_extra = (size - cols) % 2

    # Apply padding to make the image square
    new_image = np.pad(image, ((pad_rows, pad_rows + pad_rows_extra),
                               (pad_cols, pad_cols + pad_cols_extra)),
                       mode='constant', constant_values=0)
    return new_image    


def percentile_rank_limit(p_rank, p_limit):
    '''Takes the percentile rank arr of a single patient and returns 
    the cut-off value of the given percentile (the last intensity we should include)'''
    arg_lst = np.argwhere(p_rank >= p_limit)
    
    if len(arg_lst) == 0:
        return len(p_rank) - 1
    
    return arg_lst[0]


def cut_off_val(patient, p_limit):
    cumFreq = np.cumsum(patient)
    
    p_rank = (cumFreq - (0.5 * patient))/cumFreq[-1]*100

    limit_index = percentile_rank_limit(p_rank, p_limit)
    return limit_index[0]


def nifti2png():

    bad_data = read_list_from_file(BAD_DATA)

    partitions = [os.path.join(INPUT_DIR,dir) for dir in os.listdir(INPUT_DIR) if os.path.isdir(os.path.join(INPUT_DIR, dir))]

    for i, partition in enumerate(partitions):

        print_hierarchical(f"Starting work on partition \"{partition}\" ({i+1}/{len(partitions)})",1)

        #patient folders (some might not be..)
        patients = [os.path.join(partition,dir) for dir in os.listdir(partition) if (os.path.isdir(os.path.join(partition, dir)))]

        #enter each patient folder
        for i, patient in enumerate(patients):

            patient_id = patient.split("/")[-1]
            print_hierarchical(f"Converting \"{patient_id}\" ({i+1}/{len(patients)})",2)
            os.chdir(patient) 

            #converts each scan of the patient individually
            for scan in glob.glob('*.nii.gz'):

                #we do not use the mask files so we delete then
                if scan == 'mask.nii.gz':
                    os.remove(scan)
                    continue

                #make output dir for scan images
                outputdir = str.replace(scan, '.nii.gz', '')
                os.mkdir(outputdir)

                #load the .nii.gz file
                nii = nibabel.load(scan)
                niiArr = nii.get_fdata()

                #Minmaxnorm + scale as image
                if (scan.split(".")[0] == "ct"):
                    niiArr[niiArr > GLOBAL_CT_MAX] = GLOBAL_CT_MAX
                    niiArr[niiArr < GLOBAL_CT_MIN] = GLOBAL_CT_MIN

                if (scan.split(".")[0] == "mr"):
                    patient_mr_arr = np.zeros((3001))

                    for slice in range(niiArr.shape[2]):

                        if (EXCLUDE_BAD_DATA and f"{patient_id}-{slice:03}" in bad_data): 
                            continue                    
                        
                        for elm in niiArr[:, :, slice].flatten():
                            patient_mr_arr[int(elm)] += 1

                    if (sum(patient_mr_arr) == 0): # if data is so bad that no data is left, just skip it.
                        print("   Frequency array empty, skipping..")
                        continue

                    val = cut_off_val(patient_mr_arr,98)

                    niiArr[niiArr > val] = val
                    niiArr[niiArr < 0] = 0                    

                #make a .png image for each slice in the .nii file
                for slice in range(niiArr.shape[2]):

                    if (EXCLUDE_BAD_DATA and f"{patient_id}-{slice:03}" in bad_data):
                        continue

                    arr = niiArr[:, :, slice].astype(np.float32)

                    # MIN-MAX 
                    if (scan.split(".")[0] == "ct"):
                        arr = ((arr - GLOBAL_CT_MIN) * (1/(GLOBAL_CT_MAX - GLOBAL_CT_MIN)))

                    if (scan.split(".")[0] == "mr"):
                        arr = ((arr - niiArr.min()) * (1/(niiArr.max() - niiArr.min())))

                    arr = make_square(arr)        

                    tifffile.imwrite(os.path.join(outputdir, f"image{slice:03}.tiff"), arr)

                os.remove(scan)
