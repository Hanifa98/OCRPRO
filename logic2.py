from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

# Authenticate the Computer Vision client
subscription_key = os.getenv("subscription_key")
endpoint = os.getenv("endpoint")
computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))


def extract_serial_number_from_text(text: str):
    """Extract potential serial numbers from text based on predefined patterns."""
    serial_patterns = ['(s)serial number:', 's/n:']
    serial_numbers = []

    for pattern in serial_patterns:
        if pattern in text.lower():
            extracted_value = text.lower().split(pattern)[1].strip()
            if len(extracted_value) == 8:  # Assuming serial numbers are exactly 8 characters
                serial_numbers.append(extracted_value.upper())
    return serial_numbers


def extract_serial_number_from_image(image_path):
    """Extract serial numbers from an image using Azure OCR."""
    with open(image_path, 'rb') as image_stream:
        ocr_response = computervision_client.read_in_stream(image_stream, raw=True)
        operation_location = ocr_response.headers['Operation-Location']
        operation_id = operation_location.split('/')[-1]

        # Polling to wait for the OCR operation to complete
        while True:
            result = computervision_client.get_read_result(operation_id)
            if result.status not in [OperationStatusCodes.running]:
                break

        # Collect recognized serial numbers from the OCR result
        serial_numbers = []
        if result.status == OperationStatusCodes.succeeded:
            for page in result.analyze_result.read_results:
                for line in page.lines:
                    serial_numbers.extend(extract_serial_number_from_text(line.text))
        return list(set(serial_numbers))  # Remove duplicates


def rename_image_with_serial_number(image_path, serial_numbers):
    """Rename image based on extracted serial numbers."""
    directory, original_name = os.path.split(image_path)
    file_extension = original_name.split('.')[-1]
    
    # Construct new name based on serial numbers
    if len(serial_numbers) == 1:
        new_name = f"{serial_numbers[0]}.{file_extension}"
    elif len(serial_numbers) > 1:
        new_name = f"{' + '.join(serial_numbers)}.{file_extension}"
    else:
        new_name = f"unnamed.{file_extension}"  # Default if no serial numbers are found

    new_image_path = os.path.join(directory, new_name)
    os.rename(image_path, new_image_path)
    return new_name


def main(image_folder, limit=2):
    """Process images in the folder to extract and rename by serial numbers."""
    records = []

    for root, _, files in os.walk(image_folder):
        for idx, file_name in enumerate(files):
            if limit is not None:
                if idx == limit:
                    break

            image_path = os.path.join(root, file_name)
            serial_numbers = []
            log_message = f"No valid serial number found in {file_name}"
            renamed_image_path = image_path

            if os.path.isfile(image_path):
                try:
                    serial_numbers = extract_serial_number_from_image(image_path)
                    if serial_numbers:
                        new_name = rename_image_with_serial_number(image_path, serial_numbers)
                        renamed_image_path = os.path.join(root, new_name)
                        log_message = f"Success: Renamed `{file_name}` to `{new_name}`"
                    print(log_message)
                except Exception as e:
                    log_message = f"Error processing `{file_name}`: {e}"
                    print(log_message)

            records.append({
                'input_image_path': image_path,
                'serial_numbers_list': serial_numbers,
                'output_image_path': renamed_image_path,
                'log': log_message
            })

    # Create a DataFrame from the records and save to CSV
    df = pd.DataFrame(records).explode('serial_numbers_list').reset_index(drop=True)
    output_filename = f"outputs/output_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
    df.to_csv(output_filename, index=False)
    print(f'Output saved: {output_filename}')
    return df


# Run the main function
image_folder = r"C:\Users\60119\OneDrive - Bain\Desktop\LaptopSN"
limit_user_input= None  # or numbers

if __name__ == "__main__":
    df_result = main(image_folder, limit=limit_user_input)


