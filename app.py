# import os
# import fal_client
# import requests
# from flask import Flask, render_template, request, send_from_directory

# # Set the FAL_KEY environment variable in the script
# os.environ["FAL_KEY"] = "0e002174-96c8-4334-ab67-3c3bc6efede8:490b3a32ac965e52ea42f8f623bcdcdf"

# # Fetch the API key from the environment
# FAL_KEY = os.getenv("FAL_KEY")
# if not FAL_KEY:
#     raise ValueError("FAL_KEY environment variable is not set.")

# # Authenticate with the API key
# fal_client.api_key = FAL_KEY

# # Create Flask app
# app = Flask(__name__)

# # Folder for storing generated images
# STATIC_IMAGE_FOLDER = os.path.join(app.static_folder, 'images')

# # Function to get valid image size
# def get_image_size(width, height):
#     try:
#         width = int(width)
#         height = int(height)
#         if width <= 0 or height <= 0:
#             raise ValueError("Width and height must be positive integers.")
#         return width, height
#     except ValueError as e:
#         return None, str(e)

# @app.route("/", methods=["GET", "POST"])
# def index():
#     if request.method == "POST":
#         # Get the prompt and image size from the form
#         prompt = request.form["prompt"]
#         width = request.form["width"]
#         height = request.form["height"]

#         # Validate image size
#         width, height = get_image_size(width, height)
#         if not width:
#             return render_template("index.html", error=height)  # Display validation error

#         # Call the subscribe method to generate the image
#         result = fal_client.subscribe(
#             "fal-ai/flux-pro/v1.1", 
#             arguments={
#                 "prompt": prompt,
#                 "width": width,
#                 "height": height,
#             }
#         )

#         # Extract the image URL from the response
#         image_url = result['images'][0]['url']

#         # Download the image
#         response = requests.get(image_url)
#         if response.status_code == 200:
#             file_path = os.path.join(STATIC_IMAGE_FOLDER, f"generated_image_{width}x{height}.jpg")
#             if not os.path.exists(STATIC_IMAGE_FOLDER):
#                 os.makedirs(STATIC_IMAGE_FOLDER)

#             print(f"Saving image to {file_path}")
#             with open(file_path, "wb") as f:
#                 f.write(response.content)
#             return render_template("index.html", image_url=f"images/generated_image_{width}x{height}.jpg")
#         else:
#             return render_template("index.html", error="Failed to download the image.")

#     return render_template("index.html")

# # if __name__ == "__main__":
# #     app.run(debug=True)

# if __name__ == "__main__":
#     app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

from flask import Flask, render_template, send_file
import io
from PIL import Image
import requests  # If you're generating the image from an API

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')  # Serve your main UI page

@app.route('/generate-image')
def generate_image():
    # Replace this with your image generation code, e.g. an API call or some logic
    # For example, generating a simple image here:
    img = Image.new('RGB', (1920, 1080), color = (255, 0, 0))  # Red image

    # Save the image to a bytes buffer instead of a file
    img_io = io.BytesIO()
    img.save(img_io, 'JPEG')
    img_io.seek(0)

    # Return the image file for download
    return send_file(img_io, mimetype='image/jpeg', as_attachment=True, download_name='generated_image.jpg')

# if __name__ == "__main__":
#     app.run(debug=True)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
