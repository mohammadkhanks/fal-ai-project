import os
import fal_client
import io
from flask import Flask, render_template, request, send_file, redirect, url_for
import requests
from PIL import Image

# Set the FAL_KEY environment variable (if not already set)
os.environ["FAL_KEY"] = "ecb6e7bc-425e-4a2c-92eb-9b0efeabe7fd:a882593bbf7140a71a0411f9ae0a93a0"  # Insert your FAL API key here, or set it in your environment

# Fetch the API key from the environment
FAL_KEY = os.getenv("FAL_KEY")
if not FAL_KEY:
    raise ValueError("FAL_KEY environment variable is not set.")

# Authenticate with the FAL AI API key
fal_client.api_key = FAL_KEY

# Initialize Flask app
app = Flask(__name__)

# # Folder for saving generated images
# STATIC_IMAGE_FOLDER = os.path.join(app.static_folder, 'generated_images')

# # Ensure the folder exists
# os.makedirs(STATIC_IMAGE_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')  # Render the page with the button to generate the image

@app.route('/generate-image', methods=["POST"])
def generate_image():
    if request.method == "POST":
        # Get prompt and image size from the form
        prompt = request.form.get("prompt", "A beautiful landscape")  # Default prompt if not provided
        width = int(request.form.get("width", 1920))  # Default width
        height = int(request.form.get("height", 1080))  # Default height
        
        # Call the FAL AI API to generate the image based on the prompt and size
        try:
            result = fal_client.subscribe(
                "fal-ai/flux-pro/v1.1", 
                arguments={
                    "prompt": prompt,
                    "width": width,
                    "height": height,
                }
            )

            # Extract image URL from the API response
            image_url = result['images'][0]['url']
            
            # Download the image using requests
            response = requests.get(image_url)
            if response.status_code == 200:
                # Open the image in memory
                image_bytes = io.BytesIO(response.content)
                image_bytes.seek(0)  # Reset stream pointer

                # Serve the image as a downloadable file
                return send_file(
                    image_bytes,
                    mimetype='image/jpeg',
                    as_attachment=True,
                    download_name=f"generated_image_{width}x{height}.jpg"
                )
            else:
                # Pass back details for display in case of failure
                return render_template(
                    "index.html",
                    error="Failed to download the image.",
                    prompt=prompt,
                    width=width,
                    height=height
                )
        except Exception as e:
            # Pass back details for display in case of an error
            return render_template(
                "index.html",
                error=f"Error generating image: {str(e)}",
                prompt=prompt,
                width=width,
                height=height
            )

    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))