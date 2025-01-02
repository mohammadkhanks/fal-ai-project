import os
import fal_client
import io
from flask import Flask, render_template, send_file, request
import requests
from PIL import Image

# Set the FAL_KEY environment variable (if not already set)
os.environ["FAL_KEY"] = "0e002174-96c8-4334-ab67-3c3bc6efede8:490b3a32ac965e52ea42f8f623bcdcdf"  # Insert your FAL API key here, or set it in your environment

# Fetch the API key from the environment
FAL_KEY = os.getenv("FAL_KEY")
if not FAL_KEY:
    raise ValueError("FAL_KEY environment variable is not set.")

# Authenticate with the FAL AI API key
fal_client.api_key = FAL_KEY

# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')  # Render the page with the button to generate the image

@app.route('/generate-image', methods=["GET", "POST"])
def generate_image():
    if request.method == "POST":
        # Get prompt and image size from the form (if you want dynamic user inputs)
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
                # Save the image in memory
                img_io = io.BytesIO(response.content)
                img_io.seek(0)
                
                # Return the image as a downloadable file
                return send_file(img_io, mimetype='image/jpeg', as_attachment=True, download_name='generated_image.jpg')
            else:
                return render_template("index.html", error="Failed to download the image.")
        except Exception as e:
            return render_template("index.html", error=f"Error generating image: {str(e)}")

    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))