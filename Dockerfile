# Use the official Python base image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app files into the container
COPY . .

# Expose the port on which the Streamlit app will run (default is 8501)
EXPOSE 80

# Set the command to run the Streamlit app
CMD ["streamlit", "run", "--server.port",  "80", "--server.enableCORS", "false", "app.py"]
