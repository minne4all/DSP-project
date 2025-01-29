import requests
import os

# API Base URL and API Key
BASE_URL = "https://connect.aerius.nl/api/v8/utility"
API_KEY = "acca4ef0301a4f019b7a6bc99e6781d4"  # Replace with your actual API key
HEADERS = {"api-key": API_KEY}

def validate_file(file_path, strict=False):
    """
    Validate a file using the AERIUS API.
    """
    url = f"{BASE_URL}/validate"
    with open(file_path, "rb") as file:
        files = {"filePart": file}
        data = {"strict": strict}
        response = requests.post(url, headers=HEADERS, files=files, data=data)
    
    if response.status_code == 200:
        print("Validation Result:", response.json())
    else:
        print(f"Validation failed with status code {response.status_code}: {response.text}")


def validate_file_with_report(file_path, strict=False):
    """
    Validate a file and generate a report using the AERIUS API.
    """
    url = f"{BASE_URL}/validate/report"
    with open(file_path, "rb") as file:
        files = {"filePart": file}
        data = {"strict": strict}
        response = requests.post(url, headers=HEADERS, files=files, data=data)
    
    if response.status_code == 200:
        # Print the report content
        print("Validation Report:\n", response.text)
    else:
        print(f"Report generation failed with status code {response.status_code}: {response.text}")


def validate_and_convert_file(file_path):
    """
    Validate and convert a file to GML using the AERIUS API.
    """
    url = f"{BASE_URL}/validateAndConvert"
    with open(file_path, "rb") as file:
        files = {"filePart": file}
        response = requests.post(url, headers=HEADERS, files=files)
    
    if response.status_code == 200:
        result = response.json()
        if result["successful"]:
            # Decode and save the GML file
            gml_data = base64.b64decode(result["filePart"])
            gml_path = "converted_file.zip"
            with open(gml_path, "wb") as gml_file:
                gml_file.write(gml_data)
            print(f"File successfully converted and saved to {gml_path}")
        else:
            print("Validation failed with errors:", result.get("errors", []))
    else:
        print(f"Conversion failed with status code {response.status_code}: {response.text}")


def convert_file(file_path):
    """
    Convert a file to GML using the AERIUS API.
    """
    url = f"{BASE_URL}/convert"
    with open(file_path, "rb") as file:
        files = {"filePart": file}
        response = requests.post(url, headers=HEADERS, files=files)
    
    if response.status_code == 200:
        # Save the converted GML file
        gml_path = "converted_file.zip"
        with open(gml_path, "wb") as gml_file:
            gml_file.write(response.content)
        print(f"File successfully converted and saved to {gml_path}")
    else:
        print(f"Conversion failed with status code {response.status_code}: {response.text}")


if __name__ == "__main__":
    # Replace with the path to your file
    file_path = "./outputs/output.gml"
    # file_path = "./receptors/voertuigen.gml"
    
    # Validate the file
    print("Validating file...")
    validate_file(file_path, strict=True)

    # Validate the file and generate a report
    print("\nGenerating validation report...")
    validate_file_with_report(file_path, strict=True)

    # # Validate and convert the file to GML
    # print("\nValidating and converting file...")
    # validate_and_convert_file(file_path)

    # # Convert the file to GML
    # print("\nConverting file...")
    # convert_file(file_path)
