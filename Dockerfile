# Set Base Image
FROM python:3.8-alpine

# Expose the port the app runs on
EXPOSE 5000/tcp

# Set environment variables
ENV FLASK_APP=app.py

# Install system dependencies
RUN apk update && apk add --no-cache \
    python3-dev \
    gcc \
    libc-dev \
    musl-dev \
    linux-headers \
    g++

# Create necessary directories
RUN mkdir /api /json

# Copy the Python requirements file and install dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the Python scripts
COPY app.py .
COPY api/__init__.py /api/
COPY api/abis.py /api/
COPY api/config.py /api/
COPY api/eth_calls.py /api/
COPY api/main.py /api/
COPY api/task_on.py /api/
COPY api/meter_api.py /api/
COPY api/api_calls.py /api/

# Copy JSON files from the local json directory to the json directory in the container
COPY json/config.json /json/
COPY json/data.json /json/
COPY json/prices.json /json/
COPY json/borrowers.json /json/
COPY json/blocks_synced.json /json/
COPY json/lend_yields.json /json/

# Command to run the application
CMD ["python", "app.py"]
