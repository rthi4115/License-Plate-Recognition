License Plate Recognition System (Python)
Overview

-> This project implements a License Plate Recognition (LPR) system that detects vehicle number plates from images and extracts the plate text using image processing and Optical Character Recognition (OCR).

-> The solution is built using OpenCV for image preprocessing and Tesseract OCR for text extraction.
It is designed to work on regular images and can be extended to real-time video in the future.

Problem Statement

Manual identification of vehicle license numbers is time-consuming and prone to errors, especially in applications such as parking management, traffic monitoring, and security systems.

An automated solution is required to:

1.Detect license plates from images

2.Extract readable plate numbers accurately

3.Handle variations in lighting, angle, and plate size

Approach

1.The system follows a traditional computer vision pipeline:

2.Convert the input image to grayscale

3.Enhance contrast using CLAHE for better visibility

4.Reduce noise while preserving edges using bilateral filtering

5.Detect possible plate regions using a combination of:

6.Adaptive thresholding

7.Canny edge detection

8.Filter contours based on shape and aspect ratio

9.Extract the plate region and improve resolution

10.Apply Tesseract OCR to recognize characters

11.Clean and validate the extracted text

12.Duplicate detections are removed to ensure clean output.

Technologies Used

Python

OpenCV

Tesseract OCR

NumPy

Regular Expressions (re)

Project Structure
license-plate-recognition/
│
├── main.py                 # Main source code
├── README.md               # Project documentation
├── requirements.txt        # Required Python libraries
├── sample_images/          # Input test images
│   └── car1.jpg
└── output/                 # (Optional) Output images

How to Run the Project
1. Install Dependencies
pip install -r requirements.txt

2. Install Tesseract OCR

Windows: Install from the official Tesseract installer and add it to PATH

Linux:

sudo apt install tesseract-ocr

3. Run the Program
python main.py

OUTPUT:
The detected license plate and recognized text will be displayed on the image.