"""This is a python script that builds database for images from folder given on cloudinary
1. After uploading images to specific folder on cloudinary, enter the folder name here
2. Enter db_name in the end and change the insert statement accordingly.
3. Run the script
"""

import sqlite3
import cloudinary
from cloudinary.api import resources
from cloudinary.uploader import upload
import os

conn = sqlite3.connect(
    "../img_db", check_same_thread=False)
cur = conn.cursor()

# Set up your Cloudinary credentials
cloudinary.config(
  cloud_name = 'drqnkfexf',
  api_key = '127479953536276',
  api_secret = 'w-r7AP5-XtCykP61KxvWKfNr7y8'
)

# Specify the folder you want to scrape
folder_name = 'final_images'


# Set up pagination for the API request
next_cursor = None
page_size = 100
resourceS = []

'''
def upload_folder(folder_path, folder_name_in_cloudinary):
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, folder_path)
            public_id = f"{folder_name_in_cloudinary}/{relative_path}"
            result = upload(file_path, use_filename = True, unique_filename = False, folder="final_images")
            print(f"Uploaded: {file_path} => {result['secure_url']}")


local_folder_path = "resized_final/res"
cloudinary_folder_name = "final_images"

upload_folder(local_folder_path, cloudinary_folder_name)
'''

# Make API requests until all resources in the folder have been retrieved

while True:
  # Make an API request to get the next batch of resources
  response = resources(type='upload', prefix=folder_name, max_results=page_size, next_cursor=next_cursor)
  resourceS += response['resources']
  
  # Check if there are more resources to retrieve
  if 'next_cursor' in response:
    next_cursor = response['next_cursor']
  else:
    break


# Extract the URLs for each resource in the folder
image_links = [resource['secure_url'] for resource in resourceS]
#Specify the table name you want to insert data into and alter the INSERT statement accordingly

db_name = "aspect_images"

#lets clear all the data currently before inserting fresh data
#cur.execute(f"DELETE FROM {db_name}")

#lets insert values
for i in range(len(image_links)):
  link = image_links[i]
  split_link = link.split("/")
  split_link = split_link[-1][:-4]
  split_link = split_link.split("_")
  image_class = split_link[0]
  height = int(split_link[1])
  width = int(split_link[2])
  if image_class == "photo1":
     image_class = "1"
  print(split_link)
  cur.execute(f"INSERT INTO {db_name} (img_id, link, height, width, image_class) VALUES ({i+1}, \"{image_links[i]}\", {height}, {width}, {image_class});")
conn.commit()