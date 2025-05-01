# Use Python 3.12.9 as the base image
FROM python:3.12.9-slim

# Set the working directory in the container
WORKDIR /app

# Install Tesseract OCR dependencies
RUN apt-get update && \
    apt-get install -y tesseract-ocr && \
    apt-get clean

# Copy the current directory contents (from backend) into the container at /app
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Command to run the application
CMD ["python", "app.py"]
