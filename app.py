from flask import Flask, render_template, request, redirect, url_for, session, Response
import os
import fal_client
import requests
from io import BytesIO
import time

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
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")  # Set a secure key for session management

# Password for accessing the app
APP_PASSWORD = "Postman"  # Replace with your desired password

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form.get("password")
        if password == APP_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Invalid password")
    return render_template("login.html")

@app.route("/index")
def index():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("index.html")

@app.route("/generate-image", methods=["POST"])
def generate_image():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    
    # Get prompt, size, and optional seed from the form
    prompt = request.form.get("prompt", "A beautiful landscape")
    width = int(request.form.get("width", 1920))
    height = int(request.form.get("height", 1080))
    seed = request.form.get("seed", None)
    model = request.form.get("model", "Random(No Persona)")
    if seed:
        seed = int(seed)  # Ensure seed is an integer
    
    # Define model URLs
    model_urls = {
        "Random(No Persona)": None,  # Default model
        "asko_kusko": "https://v3.fal.media/files/tiger/ihSURXVXpwnok8cpsy_Cn_pytorch_lora_weights.safetensors",
        "mistik_biri": "https://v3.fal.media/files/panda/wqwyUtcau9Lvxdw6L72S6_pytorch_lora_weights.safetensors"
    }

    def generate():
        try:
            # Prepare arguments for the FAL API
            arguments = {
                "prompt": prompt,
                "width": width,
                "height": height,
                "loras": []  # Default empty loras list
            }
            
            if seed:  # Only include seed if it's provided
                arguments["seed"] = int(seed)
            
            if model != "Random(No Persona)":
                arguments["loras"].append({
                    "path": model_urls[model],
                    "scale": 1  # Default scale for lora
                })
            
            # Call the FAL AI API
            result = fal_client.subscribe(
                "fal-ai/flux-lora",
                arguments=arguments,
            )
            
            # Get the generated image URL
            image_url = result["images"][0]["url"]
            
            return render_template("index.html", 
                                   image_url=image_url,
                                   prompt=prompt, 
                                   width=width, 
                                   height=height, 
                                   seed=seed, 
                                   model=model)
        except Exception as e:
            return render_template("index.html", error=f"Error generating image: {str(e)}")
    
    return generate() 

@app.route("/logout", methods=['POST'])
def logout():
    # Remove the logged-in session and redirect to the login page
    session.pop("logged_in", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
# ================================================================================ #

# from flask import Flask, render_template, request, redirect, url_for, session
# import os
# import fal_client
# import requests
# from io import BytesIO

# # Set the FAL_KEY environment variable (if not already set)
# os.environ["FAL_KEY"] = "ecb6e7bc-425e-4a2c-92eb-9b0efeabe7fd:a882593bbf7140a71a0411f9ae0a93a0"  # Insert your FAL API key here, or set it in your environment

# # Fetch the API key from the environment
# FAL_KEY = os.getenv("FAL_KEY")
# if not FAL_KEY:
#     raise ValueError("FAL_KEY environment variable is not set.")

# # Authenticate with the FAL AI API key
# fal_client.api_key = FAL_KEY

# # Initialize Flask app
# app = Flask(__name__)
# app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")  # Set a secure key for session management

# # Password for accessing the app
# APP_PASSWORD = "Postman"  # Replace with your desired password

# @app.route("/", methods=["GET", "POST"])
# def login():
#     if request.method == "POST":
#         password = request.form.get("password")
#         if password == APP_PASSWORD:
#             session["logged_in"] = True
#             return redirect(url_for("index"))
#         else:
#             return render_template("login.html", error="Invalid password")
#     return render_template("login.html")

# @app.route("/index")
# def index():
#     if not session.get("logged_in"):
#         return redirect(url_for("login"))
#     return render_template("index.html")

# @app.route("/generate-image", methods=["POST"])
# def generate_image():
#     if not session.get("logged_in"):
#         return redirect(url_for("login"))
    
#     # Get prompt, size, and optional seed from the form
#     prompt = request.form.get("prompt", "A beautiful landscape")
#     width = int(request.form.get("width", 1920))
#     height = int(request.form.get("height", 1080))
#     seed = request.form.get("seed", None)
#     if seed:
#         seed = int(seed)  # Ensure seed is an integer
    
#     try:
#         # Prepare arguments for the FAL API
#         arguments = {
#             "prompt": prompt,
#             "width": width,
#             "height": height,
#         }
#         if seed:  # Only include seed if it's provided
#             arguments["seed"] = int(seed)

#         # Call the FAL AI API
#         result = fal_client.subscribe(
#             "fal-ai/flux-pro/v1.1",
#             arguments=arguments,
#         )
#         image_url = result["images"][0]["url"]
#         response = requests.get(image_url)
#         if response.status_code == 200:
#             # Create an in-memory file for the image
#             img_data = BytesIO(response.content)
#             img_data.seek(0)

#             # Create a unique filename based on prompt, width, height, and seed
#             filename = f"generated_image_{width}x{height}_seed_{seed or 'random'}.jpg"

#             # Serve the image URL for UI display
#             image_data = {
#                 "image_url": image_url,  # URL to display the image
#                 "filename": filename,    # Filename for download
#                 "prompt": prompt,        # Show the prompt used
#                 "width": width,          # Show image width
#                 "height": height,        # Show image height
#                 "seed": seed or "random" # Show seed or "random"
#             }
#             return render_template("index.html", **image_data)

#         else:
#             return render_template("index.html", error="Failed to fetch the image.")
#     except Exception as e:
#         return render_template("index.html", error=f"Error generating image: {str(e)}")

# @app.route("/logout", methods=['POST'])
# def logout():
#     # Remove the logged-in session and redirect to the login page
#     session.pop("logged_in", None)
#     return redirect(url_for("login"))

# if __name__ == "__main__":
#     app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))