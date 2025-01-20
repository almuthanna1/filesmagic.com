# Use a Windows base image
FROM mcr.microsoft.com/windows/servercore:ltsc2022

# Set the working directory
WORKDIR /app

# Install Chocolatey and Python
RUN powershell -Command \
    iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1')) ; \
    choco install python3 --no-progress ; \
    python -m pip install --upgrade pip ; \
    pip install -r requirements.txt

# Copy the application code
COPY . .

# Expose the application port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]
