
# Quick Start Guide for Running the Serial Number Extraction Script

## Overview
This guide will help you set up and run a script that renames images based on detected serial numbers using Azure OCR.

## Steps to Set Up

### 1. Prerequisites
- **Python 3.6+** installed.
- An **Azure Computer Vision API** account (get your subscription key and endpoint URL).

### 2. Installation
1. **Download the project files** and open the folder.
2. **Create a virtual environment** (a separate environment to keep things organized):
   - In the command line, type:
     ```
     python -m venv venv
     ```
3. **Activate the virtual environment**:
   - On Windows:
     ```
     .\venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```
4. **Install required packages**:
   ```
   pip install -r requirements.txt
   ```

### 3. Configure Your Azure Credentials
1. In the project folder, open the `.env` file (or create one if missing).
2. Add your Azure details:
   ```
   subscription_key=<Your_Azure_Subscription_Key>
   endpoint=<Your_Azure_Endpoint>
   ```

### 4. Running the Script
1. Place the images you want to process in a folder.
2. Open the script file and edit these two lines near the end:
   ```python
   image_folder = r"<Your_Image_Folder_Path>"
   limit_user_input = <Number_of_Files_to_Process_or_None>
   ```
   - Replace `<Your_Image_Folder_Path>` with the path to your folder of images.
   - Set `limit_user_input` to how many images you want to process (or `None` for all).

3. **Run the script**:
   ```
   python script.py
   ```

### 5. Output
- Renamed images will appear in the original folder.
- A CSV file with details will save in the `outputs` folder.

## Troubleshooting
- Make sure the `.env` file has the correct Azure credentials.
- Activate the virtual environment before running (`venv`).

That's it! You are ready to go.
