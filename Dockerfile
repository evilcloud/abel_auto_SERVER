# Use an appropriate base image
FROM python:3.7

# Set the working directory
WORKDIR /app

# Copy the necessary files into the container
COPY api /app/api
COPY dashboard /app/dashboard
COPY data /app/data

# Install dependencies for API service
WORKDIR /app/api
RUN pip install -r requirements.txt

# Install dependencies for Dashboard service
WORKDIR /app/dashboard
RUN pip install -r requirements.txt

# Expose the necessary ports
EXPOSE 8000
EXPOSE 8501

# Start the services
CMD ["python", "api.py"]
