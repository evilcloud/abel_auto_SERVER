# Base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements.txt file
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the dashboard.py file
COPY dashboard.py .

# Expose the port
EXPOSE 8501

# Set the entrypoint command
CMD ["streamlit", "run", "--server.port", "8501", "dashboard.py"]
