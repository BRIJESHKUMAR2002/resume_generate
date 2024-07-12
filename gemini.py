import os
import json
import subprocess
from docxtpl import DocxTemplate
from dotenv import load_dotenv
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
import vertexai.preview.generative_models as generative_models
import re

current_file_directory = os.path.dirname(os.path.abspath(__file__))
print("Current File Directory:", current_file_directory)

load_dotenv()
os.environ[
    "GOOGLE_APPLICATION_CREDENTIALS"] = f"{current_file_directory}/resume code/rugged-silo-426214-k4-e55412882921.json"

folder = f"{current_file_directory}/processed/"
new_folder = f"{current_file_directory}/pdf_processed/"


def convert_docx_to_pdf(docx_path, new_folder):
    print('-----------------------conversion')
    try:
        print('-----------------------try_conversion')
        result = subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', '--outdir', new_folder, docx_path],
                                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Conversion successful.")
        print("stdout:", result.stdout.decode())
        print("stderr:", result.stderr.decode())
    except subprocess.CalledProcessError as e:
        print("Error during conversion:", e)
        print("stdout:", e.stdout.decode())
        print("stderr:", e.stderr.decode())


def gemini_process(Input, filename, template):
    filename = os.path.splitext(filename)[0]
    print("Filename : ",filename)
    # Initialize Vertex AI with your project and locationlo
    vertexai.init(project="genaiform", location="europe-west2")

    # Define the generation configuration
    generation_config = GenerationConfig(
        temperature=0,
        top_p=0,
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
        model_name="gemini-1.5-flash-001",
        system_instruction="""You are an expert resume writer. Use the data provided by the user to create a polished 
        and professional resume. Enhance the resume with additional relevant details and phrasing to ensure it stands 
        out."""
    )

    # Define the prompt
    text1 = """
    You are tasked with analyzing the provided Input and extracting relevant text values for specified entities.
    Follow the given JSON schema accurately to ensure all details are correctly captured. If a field is not present,
    use the default value as JSON Schema.
    
    Guidelines for extraction and formatting:
     - Do not alter or change data or make assumptions , extract all text values.
    - Keep same language as input.
    - Strip all non-standard characters (e.g., bullet points, newline characters, tabs) from the extracted data.
    - If Name or Company name are all caps, reformat them to only capitalize the first letter
    - If End_Year or End_Year_month is to-date then replace to-date with Present.
    - Do not repeat information under Employment_History either list it under Description or Responsibilities_and_Achievements.
    - Fix spacing between words
    - For 'Employment_History', if a month is present, extract and convert into short form (e.g., Jan, Feb, Mar, Aug, Sep, Oct, Nov, Dec), if numeric such as 01/2002  then it shoud be Jan 2002, if no month mentioned list only year.
    - Only for CV_Summary extract Start Year and End Year without month.
   
    Input:
    {}

    Output:
    The output should strictly adhere to the following JSON schema:
    """

    json_schema = """{
      "Candidate_name": { "type": "string","default": ""},
      "Candidate_first_name": { "type": "string","default": ""},
      "Candidate_last_name": { "type": "string","default": ""},
      "Date_of_birth":{ "type": "string","default": ""},
      "Nationality":{ "type": "string","default": ""},
      "Education": { "type": "string","default": ""},
      "Residence": { "type": "string","default": ""},
      "Current_company": { "type": "string","default": ""},
      "Current_position": { "type": "string","default": ""},
      "Compensation": { "type": "string","default": ""},
      "CV_Summary": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "Start_Year": { "type": "string","default": ""},
            "End_Year": { "type": "string","default": ""},
            "Company_name": { "type": "string","default": ""},
            "Position_title": { "type": "string","default": ""}
          },
          "required": ["Start_Year", "End_Year", "Company_name", "Position_title"]
        }
      },
      "Personal_Profile": { "type": "string" },
      "Employment_History": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "Company_name": { "type": "string" },
            "Start_Year_month": { "type": "string" },
            "End_Year_month": { "type": "string" },
            "Job_title": { "type": "string" },
            "Location": { "type": "string" },
            "Description": { "type": "string" },
            "Key_Responsibilities_and_Achievements": {
              "type": "array",
              "items": { "type": "string" }
            }
          },
          "required": ["Company_name", "Start_Year_month", "End_Year_month", "Job_title"]
        }
      },
      "Education_details": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "Institution": { "type": "string" },
            "Location": { "type": "string"},
            "Year": { "type": "string", "default": ""},
            "Start_Year": { "type": "string" },
            "End_Year": { "type": "string" },
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
    # Remove the backticks and clean the response text
    cleaned_response_text = data.replace('```json', '').replace('```', '').strip()

    def clean_json_string(json_string):
        # Remove any invalid control characters
        return re.sub(r'[\x00-\x1f\x7f]', '', json_string)

    def parse_json_response(response_text):
        try:
            # Clean the response text
            cleaned_text = clean_json_string(response_text)
            # Load the cleaned response text into a JSON object
            pretty_json = json.loads(cleaned_text)
            # Pretty print the JSON data
            pretty_json_str = json.dumps(pretty_json, indent=4)
            print("pretty_json_str : ", pretty_json_str)
            return pretty_json
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print("Response text after cleaning:")
            print(response_text)
            return None

    # Parse the cleaned response text
    pretty_json = parse_json_response(cleaned_response_text)

    # output_folder = 'processed/'

    if pretty_json:
        # Load the template
        template_path = f'{current_file_directory}/data/{template}.docx'
        doc = DocxTemplate(template_path)
        doc.render(pretty_json)
        filename_with_extension = filename + ".docx"
        output_path = os.path.join(folder, filename_with_extension)
        doc.save(output_path)
        convert_docx_to_pdf(output_path, new_folder)
    else:
        print("Failed to parse JSON response.")

    return
