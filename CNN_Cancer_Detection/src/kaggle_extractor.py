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