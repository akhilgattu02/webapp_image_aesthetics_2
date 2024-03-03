import cloudinary
import cloudinary.uploader
import cloudinary.api

cloudinary.config(
  cloud_name = 'drqnkfexf',
  api_key = '127479953536276',
  api_secret = 'w-r7AP5-XtCykP61KxvWKfNr7y8'
)

folder_name = "audios"
max_results = 100

# Initialize the cursor to None
next_cursor = None

# Loop through all pages of results
while True:
    # Get a page of results
    print("loop1")
    response = cloudinary.api.resources(type="upload", prefix=folder_name, max_results=max_results, next_cursor=next_cursor)

    # Loop through each file on this page and get its public ID and duration
    for item in response["resources"]:
        print("loop2")
        public_id = item["public_id"]
        url = cloudinary.utils.cloudinary_url(public_id, resource_type="raw")
        duration = item["duration"]
        
        print("File: " + public_id)
        print("URL: " + url[0])
        print("Duration: " + str(duration) + " seconds")
    
    # If there are no more pages, break out of the loop
    if "next_cursor" not in response:
        break
    
    # Otherwise, set the cursor to the next page of results
    next_cursor = response["next_cursor"]