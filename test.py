import base64
import vertexai
from dotenv import load_dotenv
from vertexai.generative_models import GenerativeModel, Part
import os

load_dotenv()
current_file_directory = os.path.dirname(os.path.abspath(__file__))
os.environ[
    "GOOGLE_APPLICATION_CREDENTIALS"] = f"{current_file_directory}/resume code/rugged-silo-426214-k4-e55412882921.json"

vertexai.init(project="genaiform", location="europe-west2")

model = GenerativeModel(model_name="gemini-1.5-flash-001")

image_file_uri = "images.jpeg"  # Replace with your image file path

with open(image_file_uri, 'rb') as file:
    binary_data = file.read()
    base64_encoded_data = base64.b64encode(binary_data)
    encoded_string = base64_encoded_data.decode('utf-8')

response = model.generate_content(
    [
        Part.from_uri(
            encoded_string,
            mime_type="image/jpeg",
        ),
        "What is shown in this image?",
    ]
)

print(response.text)
