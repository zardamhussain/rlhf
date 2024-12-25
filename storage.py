import os
import time
from PIL import Image, ImageFile
from appwrite_client import client
from appwrite.id import ID
from appwrite.services.storage import Storage
from appwrite.input_file import InputFile
from appwrite.query import Query
from db import check_image_exists, create_image_document, is_image_labled
import io

images_storage_id = "676ac08e00295a53cf2e"
images_folder = "./Celebrity images"
storage = Storage(client)

def upload_files_from_folder(folder_path, storage, bucket_id):
    """
    Uploads all files in the given folder to the storage system.
    
    Parameters:
    - folder_path: Path to the folder containing the files.
    - storage: The storage system instance (assumed to have a `create_file` method).
    - bucket_id: ID of the storage bucket to upload to.
    """
    # Ensure the folder exists
    if not os.path.isdir(folder_path):
        print(f"The folder {folder_path} does not exist.")
        return

    # Loop through all files in the folder

    for filename in os.listdir(folder_path):
        print(f"Found file: {filename}")
        file_path = os.path.join(folder_path, filename)
        
        # Skip directories, only process files
        if os.path.isdir(file_path):
            continue
        
        try:
            # Open the file in binary mode
            with open(file_path, 'rb') as file:
                file_data = file.read()
                
                # Upload the file to the storage system
                print(f"Uploading {filename}")
                storage.create_file(
                    bucket_id=bucket_id,
                    file_id=ID.unique(),  # Generate a unique ID for the file
                    file=InputFile().from_bytes(file_data, filename)
                )
                time.sleep(0.2)
                print(f"Successfully uploaded: {filename}")
        
        except Exception as e:
            print(f"Failed to upload {filename}: {e}")

# upload_files_from_folder(images_folder, storage, images_storage_id)

# response = storage.list_files(bucket_id=images_storage_id) # retuns only 25
# for file in response['files']:
#     if not check_image_exists(file['$id']):
#         print(f"Adding {file['name']} to database", file['$id'])
#         create_image_document(file['$id'])

def list_images(offset, limit):
    try:
        response = storage.list_files(bucket_id=images_storage_id, queries=[Query.offset(offset), Query.limit(limit)])
        image_ids = []
        for file in response['files']:
            if not check_image_exists(file['$id']):
                print(f"Adding {file['name']} to database", file['$id'])
                create_image_document(file['$id'])
                image_ids.append((file['$id'], False))
            else:

                image_ids.append((file['$id'], is_image_labled(file['$id']))) 
        
        # total_count, [(image_id, isLabled)]
        return response["total"], image_ids
    
    except Exception as e:
        print(f"Error fetching data: {e}")
        return 0, []
    
def get_image(image_id):    
    try:
        # response = storage.get_file(bucket_id=images_storage_id, file_id=image_id)
        res = storage.get_file_download(bucket_id=images_storage_id, file_id=image_id)
        return Image.open(io.BytesIO(res),)
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None
    
# get_image("676ad0ce7c9ba0862d55")