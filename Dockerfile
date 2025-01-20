# Use a Linux base image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Expose port 8080
EXPOSE 8080

# Command to run the app
CMD ["python", "app.py"]
