# Use an official Python runtime as a parent image
FROM --platform=linux/amd64 python:3.8-slim-buster as build
# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV FLASK_APP=app.py

# Run app.py when the container launches
ENTRYPOINT ["python3"]
CMD ["-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]
