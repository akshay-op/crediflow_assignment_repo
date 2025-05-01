# Use Python 3.12.9 base image
FROM python:3.12.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies (Tesseract OCR)
RUN apt-get update && \
    apt-get install -y tesseract-ocr && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy your backend code into the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port (optional, good for documentation)
EXPOSE 5000

# Command to run your Flask app with Gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
