from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
import os
import re
from pathlib import Path
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()


# Authenticate the Computer Vision client
subscription_key = os.environ["subscription_key"]
endpoint = os.environ["endpoint"]
computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))


def text2serialnumber(text: str):
    potential_keys = ['(s)serial number:', 's/n:']
    matches = []
    for key in potential_keys:
        if key in text.lower():
            value = text.lower().split(key)[1].strip()
            if len(value) == 8:
                matches.append(value)
    matches = [match.upper() for match in matches]
    return matches

# Function to extract serial numbers from image based on "S/N" or "Serial Number" labels
def extract_serial_number_from_image(image_path):
    with open(image_path, 'rb') as image_stream:
        # Send the image to the Azure OCR service
        ocr_result = computervision_client.read_in_stream(image_stream, raw=True)
        operation_location = ocr_result.headers['Operation-Location']
        operation_id = operation_location.split('/')[-1]

        # Wait for the OCR operation to complete
        result = computervision_client.get_read_result(operation_id)
        while result.status == OperationStatusCodes.running:
            result = computervision_client.get_read_result(operation_id)

        # Extract the recognized text and find serial numbers that follow "S/N" or "Serial Number"
        serial_numbers = []
        if result.status == OperationStatusCodes.succeeded:
            for page in result.analyze_result.read_results:
                for line in page.lines:
                    matches = text2serialnumber(line.text)
                    if matches:
                        serial_numbers.extend(matches)
        # Remove duplicates by converting to a set and back to a list
        serial_numbers = list(set(serial_numbers))
        return serial_numbers

# Function to rename image based on serial numbers
def rename_image(image_path, serial_numbers):
    image_dir, image_name = os.path.split(image_path)
    image_extension = image_name.split('.')[-1]

    # Create the new file name using the valid serial numbers only, without duplicates
    if len(serial_numbers) == 1:
        new_image_name = f"{serial_numbers[0]}.{image_extension}"
    elif len(serial_numbers) > 1:
        new_image_name = f"{' + '.join(serial_numbers)}.{image_extension}"
    else:
        new_image_name = f"unnamed.{image_extension}"  # In case no serial number is found

    new_image_path = os.path.join(image_dir, new_image_name)
    os.rename(image_path, new_image_path)
    return new_image_name


def main(image_grand_folder=None, limit=2):
    image_path_ls = []
    serial_numbers_ls = []
    output_path_ls = []
    logs_ls = []

    for root, _, files in os.walk(image_grand_folder):
        for idx, image_file in enumerate(files):
            image_path = os.path.join(root, image_file)
            new_image_path = image_path

            try:
                if os.path.isfile(image_path):
                    serial_numbers = extract_serial_number_from_image(image_path)
                    # Only rename the image if valid serial numbers are found after "S/N" or "Serial Number"
                    print(f'#### image path: {image_path}')
                    if serial_numbers:
                        print(f'#### serial_numbers: {serial_numbers}')

                        new_image_name = rename_image(image_path, serial_numbers)
                        message = f"Successs: Renamed `{image_file}` to `{new_image_name}`"
                        print(message)
                    else:
                        message = f"No valid serial number found in {image_file}"
                        print(message)
            except Exception as e:
                message = f'Error. Image path: {image_path} | Error message: {e}'
                print(message)

            image_path_ls.append(image_path)
            serial_numbers_ls.append(serial_numbers)
            output_path_ls.append(new_image_path)
            logs_ls.append(message)

            if idx == limit:
                break


    df = pd.DataFrame({'input_image_path':image_path_ls,
                        'serial_numbers_list':  serial_numbers_ls,
                        'output_image_path': output_path_ls,
                        'logs': logs_ls})


    df_exploded = df.explode('serial_numbers_list').reset_index(drop=True)

    now = datetime.now()
    formatted_datetime = now.strftime("%Y-%m-%d_%H-%M-%S")
    output_file_name = f"output_{formatted_datetime}"
    df_exploded.to_csv(f'{output_file_name}.csv', index=False)
    print(f'Output saved: {output_file_name}')
    return df_exploded


image_grand_folder = r"C:\Users\60119\OneDrive - Bain\Desktop\LaptopSN"
df_exploded = main(image_grand_folder)

