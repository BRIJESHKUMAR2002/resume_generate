import os
import json
import subprocess
from docxtpl import DocxTemplate
from dotenv import load_dotenv
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
import vertexai.preview.generative_models as generative_models
import re

load_dotenv()
os.environ[
    "GOOGLE_APPLICATION_CREDENTIALS"] = "/home/tech/Documents/RESUME PROJECT/resume code/rugged-silo-426214-k4-e55412882921.json"

folder = "processed/"


def gemini_process(Input, filename):
    # Initialize Vertex AI with your project and location
    vertexai.init(project="rugged-silo-426214-k4", location="europe-west2")

    # Define the generation configuration
    generation_config = GenerationConfig(
        temperature=0,
        top_p=0.1,
        top_k=1,
    )

    # Define safety settings
    safety_settings = {
        generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    }

    # Create a GenerativeModel instance
    model = GenerativeModel(
        "gemini-1.5-flash-001",
    )

    # Define the prompt
    text1 = """
    You are tasked with analyzing the provided Input and extracting relevant text values for specified entities.
    Follow the given JSON schema accurately to ensure all details are correctly captured. If a field is not present,
    use the default value specified in the schema.

    Input:
    {}

    Output:
    The output should strictly adhere to the following JSON schema:
    """

    json_schema = """{
      "Candidate_name": { "type": "string", "default":null },
      "Education": { "type": "string", "default":null},
      "Residence": { "type": "string", "default":null },
      "Current_company": { "type": "string", "default":null },
      "Current_position": { "type": "string", "default":null },
      "Compensation": { "type": "string", "default": null },
      "CV_Summary": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "Start_Month_Year": { "type": "string" },
            "End_Month_Year": { "type": "string" },
            "Company_name": { "type": "string" },
            "Position_title": { "type": "string" }
          },
          "required": ["Start_Month_Year", "End_Month_Year", "Company_name", "Position_title"]
        }
      },
      "Personal_Profile": { "type": "string" },
      "Employment_History": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "Company_name": { "type": "string" },
            "Start_Month_Year": { "type": "string" },
            "End_Month_Year": { "type": "string" },
            "Job_title": { "type": "string" },
            "Location": { "type": "string" },
            "Description": { "type": "string" },
            "Key_Responsibilities_and_Achievements": {
              "type": "array",
              "items": { "type": "string" }
            }
          },
          "required": ["Company_name", "Start_Month_Year", "End_Month_Year", "Job_title"]
        }
      },
      "Education_details": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "Institution": { "type": "string" },
            "Location": { "type": "string", "default": null },
            "Year": { "type": "string" },
            "Degree": { "type": "string" }
          },
          "required": ["Institution", "Degree"]
        }
      },
      "Certifications_courses": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "Certification_name": { "type": "string" },
            "Issuing_organization": { "type": "string" },
            "Year_of_issuance": { "type": "string" }
          },
          "required": ["Certification_name", "Issuing_organization"]
        }
      },
      "Additional_information": {
        "type": "object",
        "properties": {
          "Skills": { "type": "array", "items": { "type": "string" } },
          "Training_and_awards": { "type": "array", "items": { "type": "string" } },
          "Interests": { "type": "array", "items": { "type": "string" } },
          "Languages": { "type": "array", "items": { "type": "string" } }
        }
      },
      "required": [
        "Candidate_name", "Residence", "Education", "Current_company", "Current_position",
        "CV_Summary", "Personal_Profile", "Employment_History", "Education_details", "Additional_information"
      ]
    }"""
    # Generate content using the model
    response = model.generate_content(
        contents=[text1, Input, json_schema],
        generation_config=generation_config,
        safety_settings=safety_settings
    )

    # Print the response
    data = response.text
    print(type(data))
    print(data)

    # Remove the backticks and clean the response text
    cleaned_response_text = data.replace('```json', '').replace('```', '').strip()
    print("Cleaned response text:")
    print(cleaned_response_text)

    def clean_json_string(json_string):
        # Remove any invalid control characters
        return re.sub(r'[\x00-\x1f\x7f]', '', json_string)

    def parse_json_response(response_text):
        try:
            # Clean the response text
            cleaned_text = clean_json_string(response_text)
            # Load the cleaned response text into a JSON object
            pretty_json = json.loads(cleaned_text)
            print("JSON data loaded successfully:")
            # Pretty print the JSON data
            pretty_json_str = json.dumps(pretty_json, indent=4)
            print(pretty_json_str)
            return pretty_json
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print("Response text after cleaning:")
            print(response_text)
            return None

    # Parse the cleaned response text
    pretty_json = parse_json_response(cleaned_response_text)

    def convert_docx_to_pdf(docx_path, output_folder):
        try:
            # Make sure LibreOffice is installed and the `soffice` command is in your PATH
            subprocess.run(['soffice', '--convert-to', 'processed', '--outdir', output_folder, docx_path], check=True)
            print("Conversion successful.")
        except subprocess.CalledProcessError as e:
            print("Error during conversion:", e)

    if pretty_json:
        # Load the template
        template_path = '/home/tech/Documents/RESUME PROJECT/data/Template_edit.docx'
        doc = DocxTemplate(template_path)

        # Render the document with Jinja2 context
        doc.render(pretty_json)

        # Save the updated document
        output_path = os.path.join(folder, filename)
        doc.save(output_path)
        convert_docx_to_pdf(output_path, "/home/tech/Documents/RESUME PROJECT/processed")
    else:
        print("Failed to parse JSON response.")

    return


