from flask import Flask, render_template, request, send_file, redirect, url_for, session, make_response
import os
import fal_client
import requests
from io import BytesIO

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
APP_PASSWORD = "yourpassword"  # Replace with your desired password

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
    if seed:
        seed = int(seed)  # Ensure seed is an integer
    
    try:
        # Call the FAL AI API
        result = fal_client.subscribe(
            "fal-ai/flux-pro/v1.1",
            arguments={
                "prompt": prompt,
                "width": width,
                "height": height,
                "seed": seed,
            },
        )
        image_url = result["images"][0]["url"]
        response = requests.get(image_url)
        if response.status_code == 200:
            # Create an in-memory file for the image
            img_data = BytesIO(response.content)
            img_data.seek(0)

            # Provide download link with additional info
            filename = f"generated_image_{width}x{height}_seed_{seed or 'random'}.jpg"
            return send_file(
                img_data,
                as_attachment=True,
                download_name=filename,
                mimetype="image/jpeg",
            )
        else:
            return render_template("index.html", error="Failed to fetch the image.")
    except Exception as e:
        return render_template("index.html", error=f"Error generating image: {str(e)}")

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))