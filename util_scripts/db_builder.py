"""This is a python script that builds database for images from folder given on cloudinary
1. After uploading images to specific folder on cloudinary, enter the folder name here
2. Enter db_name in the end and change the insert statement accordingly.
3. Run the script
"""

import sqlite3
import cloudinary
from cloudinary.api import resources

conn = sqlite3.connect(
    "img_db", check_same_thread=False)
cur = conn.cursor()

# Set up your Cloudinary credentials
cloudinary.config(  
  cloud_name = 'drqnkfexf',
  api_key = '127479953536276',
  api_secret = 'w-r7AP5-XtCykP61KxvWKfNr7y8'
)

# Specify the folder you want to scrape
folder_name = 'aspect_ratio'

# Set up pagination for the API request
next_cursor = None
page_size = 100
resourceS = []
  
# Make API requests until all resources in the folder have been retrieved
while True:
  # Make an API request to get the next batch of resources
  response = resources(type='upload', prefix=folder_name, max_results=page_size, next_cursor=next_cursor)
  # print(response)
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
cur.execute(f"DELETE FROM {db_name}")

#lets insert values
for i in range(len(image_links)):
  print(image_links[i])
  cur.execute(f"INSERT INTO {db_name} (img_id,link) VALUES ({i+1},\"{image_links[i]}\");")

conn.commit()