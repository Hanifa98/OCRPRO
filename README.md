
# Documentation for Serial Number Extraction and Image Renaming Script

## Overview

This Python script uses Azure Cognitive Services' OCR (Optical Character Recognition) to scan images for serial numbers and rename the image files based on detected serial numbers. The renamed files are stored in a designated folder with a record of processed files and any extracted serial numbers saved in a CSV file.

The primary components of this project are:
- **Computer Vision Client Authentication**: Authenticating with Azure Computer Vision.
- **OCR for Serial Number Detection**: Using OCR to identify and extract serial numbers in images.
- **Image Renaming**: Renaming images based on detected serial numbers.
- **Logging and Saving Results**: Saving the output records in a CSV file for tracking and validation purposes.

## Project Setup

### Prerequisites

Ensure you have:
1. **Azure Computer Vision API** with a valid subscription key and endpoint.
2. **Python 3.6+** installed.
3. Required Python libraries specified in `requirements.txt`:
   - `azure-cognitiveservices-vision-computervision`
   - `msrest`
   - `pandas`
   - `python-dotenv`

### Project Structure

The project directory includes:
- `.env`: Stores sensitive data like the Azure subscription key and endpoint.
- `requirements.txt`: Lists required packages.
- `.gitignore`: Ignores unnecessary files like virtual environments, `.env`, and output folders.
- `outputs/`: Folder where the CSV output file will be saved.
- `venv/`: Virtual environment created with `python -m venv venv` for package management and isolation.

### Installation Steps

1. **Clone the repository** or download the script.
2. **Set up the virtual environment**:
   ```bash
   python -m venv venv
   ```
3. **Activate the virtual environment**:
   - On Windows:
     ```bash
     .\venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
5. **Configure the .env file**:
   Create a `.env` file in the root folder with the following content:
   ```plaintext
   subscription_key=<your_subscription_key>
   endpoint=<your_endpoint_url>
   ```
   Replace `<your_subscription_key>` and `<your_endpoint_url>` with your Azure credentials.

### Usage

Run the script from the command line:
```bash
python script.py
```

### Parameters

- `image_folder`: The path to the folder containing images to be processed.
- `limit`: Limits the number of images to process (default is `2`). Set to `None` to process all images.

## Script Walkthrough

### Imports

Imports required modules and packages, including `azure.cognitiveservices`, `pandas`, `datetime`, and `dotenv`.

### Authentication

The script loads environment variables from `.env` to authenticate with Azure's Computer Vision API. The `ComputerVisionClient` is initialized using the subscription key and endpoint.

```python
subscription_key = os.getenv("subscription_key")
endpoint = os.getenv("endpoint")
computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))
```

### Functions

#### 1. `extract_serial_number_from_text(text: str)`

Extracts serial numbers from a given text based on patterns like "serial number" or "s/n:". It returns serial numbers that match these patterns and are exactly 8 characters long.

#### 2. `extract_serial_number_from_image(image_path)`

Reads an image file, sends it to Azure OCR, and retrieves any detected serial numbers. The function:
- Sends the image to Azure OCR.
- Polls until OCR results are returned.
- Calls `extract_serial_number_from_text` to identify and extract serial numbers.

#### 3. `rename_image_with_serial_number(image_path, serial_numbers)`

Renames an image based on the extracted serial numbers:
- If a single serial number is detected, the image is renamed accordingly.
- If multiple serial numbers are detected, they are concatenated.
- If no serial number is found, a default name (`unnamed`) is assigned.

#### 4. `main(image_folder, limit=2)`

Processes all images in a specified folder:
- Iterates over images, extracts serial numbers, renames files, and logs results.
- Saves a record of each image’s original path, extracted serial numbers, renamed path, and processing log.
- Generates a timestamped CSV file in the `outputs/` folder to store the results.

### Example

```python
image_folder = r"C:\path\to\images"
limit_user_input = 2  # or None to process all images

if __name__ == "__main__":
    df_result = main(image_folder, limit=limit_user_input)
```

## Output

The script outputs:
1. **Renamed Image Files**: The files in the `image_folder` will be renamed based on detected serial numbers.
2. **CSV Log**: The `outputs/` folder will contain a CSV file named `output_<timestamp>.csv` with columns:
   - `input_image_path`: Original image path.
   - `serial_numbers_list`: List of detected serial numbers.
   - `output_image_path`: Path of the renamed image.
   - `log`: Log message for each image processed.

## Error Handling

The script handles errors during image processing and logs them in the CSV file under the `log` column, allowing for troubleshooting without interrupting batch processing.

## Additional Notes

- **Environment Management**: Always activate the virtual environment before running the script to ensure dependencies are managed correctly.
- **Azure Rate Limits**: Ensure that your Azure subscription can handle the volume of OCR requests, as rate limits may apply.
