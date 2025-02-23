# Use the official Python image as the base image
FROM --platform=linux/x86_64 python:3.12.4-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt into the container
COPY requirements.txt .

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Clean the cache
RUN pip cache purge && \
    rm -rf /root/.cache/pip

# Set the default command to run your scripts using a shell script
COPY run.sh ./scripts/
RUN chmod +x /app/scripts/run.sh

# Copy the source code
COPY src/ ./src/
