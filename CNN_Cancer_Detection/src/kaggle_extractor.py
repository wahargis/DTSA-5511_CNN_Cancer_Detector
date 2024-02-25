"""
A small module for fetching Kaggle competition datasets
"""

import os
import re
import kaggle
import requests
import urllib.parse
import zipfile

def convert_byte_size_to_bytes(byte_size_str):
    # Regular expression to extract numeric and unit parts
    match = re.match(r'^(\d+)([KMGT]B)?$', byte_size_str, re.IGNORECASE)

    if match:
        # Extract the numeric part and unit part
        numeric_part = int(match.group(1))
        unit_part = match.group(2)

        # Define conversion factors for different units (KB, MB, GB, TB)
        units = {'KB': 1024, 'MB': 1024**2, 'GB': 1024**3, 'TB': 1024**4}

        # Convert to bytes
        if unit_part:
            unit_part = unit_part.upper()  # Convert unit to uppercase for case-insensitive matching
            if unit_part in units:
                return numeric_part * units[unit_part]
            else:
                raise ValueError(f"Unsupported unit: {unit_part}")
        else:
            return numeric_part

    else:
        raise ValueError("Invalid byte size format")

def Kaggle_Data_Pull(competition_name = 'histopathologic-cancer-detection', usr_path='./data/', file_return=False):
        # has some pagination issue, only grabs up to 20 files per directory
        # eg. if dataset is
        """
        competition_data/
            ∟/train/...
            ∟/test/...
            ∟train_labels.csv
            ∟test_labels.csv
        """
        # then it will pull 42 items; 4 items from competition_data of which 2 items are /train/ and /test/ each holding 20 entries within them
        print("Grabbing file names from Kaggle...")
        files = kaggle.api.competition_list_files(competition_name)
        file_names = [i.name for i in files]
        file_sizes = [i.size for i in files]
    
        print('Downloading from Kaggle...')
        for file, size in zip(file_names, file_sizes):
            
            kaggle.api.competition_download_file(competition_name, file, usr_path)
            
            if convert_byte_size_to_bytes(size) >= convert_byte_size_to_bytes('1MB'):
                file = file + '.zip'
            else:
                pass
                
            file = urllib.parse.quote(file)
            
            if file.endswith('.zip'):
                print(f"Extracting '{file}'...")
                with zipfile.ZipFile(usr_path + file, 'r') as zip_ref:
                    zip_ref.extractall(usr_path)  # Extract to the current directory or specify a different path
                print(f"Finished extracting '{file}'.")
            
            print(f"Files pulled to: {os.getcwd()}")
            
        for root, _, files in os.walk(usr_path):
            for filename in files:
                # Full path to the file
                file_path = os.path.join(root, filename)
    
                # Decode the filename to remove URL-encoded characters
                decoded_filename = urllib.parse.unquote(filename)
    
                # Get new file name
                new_file_path = os.path.join(root, decoded_filename)
                
                # Check if the renamed file already exists
                if os.path.exists(new_file_path):
                    print(f"File '{decoded_filename}' already exists, skipping.")
                else:
                    #Rename the file
                    os.rename(file_path, new_file_path)
                    # Print the renaming operation
                    print(f"Renamed '{filename}' to '{decoded_filename}'")
                    
        if file_return:
            return files
def get_y_n_input(input_str):
    while True:
        usr = input(input_str)
        try:
            if usr.upper() == "Y":
                usr_flag = False
                break
            elif usr.upper() == "N":
                usr_flag = True
                break
            else:
                raise ValueError
        except ValueError:
            print("Invalid Input")
            continue
    return usr_flag

#alternate method without pagination issue, using os.system call to cli API...
def Kaggle_Competition_Extract(competition_name):
    try:
        if os.path.exists("./data"):
            os.chdir("./data")
        else:
            print("Making /data/ subfolder")
            os.mkdir("./data")
            os.chdir("./data")
        
        files = kaggle.api.competition_list_files(competition_name)
        file_names = [i.name for i in files]
        last_file = file_names[-1]
        last_file_path = os.path.join(os.getcwd(), last_file)
        file_flag = False
        if os.path.exists(last_file_path):
            input_str = "Files may already be present... \n Download anyway? \n[Y]es/[N]o"
            file_flag = get_y_n_input(input_str)
        zip_path = os.path.join(os.getcwd(), competition_name+".zip")
        if os.path.exists(zip_path) or file_flag:
            print("Competition files already downloaded...")
        else:
            print("Downloading competition files...")
            os.system("kaggle competitions download -c histopathologic-cancer-detection")
            print("Competition files downloaded.")
            
        if file_flag:
            pass
        else:
            with zipfile.ZipFile(zip_path, mode='r') as zip_ref:
                first_in_zip = zip_ref.namelist()[0]
                last_in_zip = zip_ref.namelist()[-1]
                if os.path.exists(os.path.join(os.getcwd(), first_in_zip)) and os.path.exists(os.path.join(os.getcwd(), last_in_zip)):
                    print("Zipped files already present in /data/...")
                else:
                    print("Extracting files...")
                    zip_ref.extractall(os.getcwd())
                    print("Files extracted")
        if os.path.exists(zip_path):
            print("Cleaning up data directory...")
            os.remove(zip_path)
        os.chdir("..")
        print("\nData directory ready!")
    except Exception as e:
        os.chdir("..")
        print(f"Exception occurred: \n{e}")