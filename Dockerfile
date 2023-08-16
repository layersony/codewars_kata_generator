# Use the official Python image as the base image
FROM python:3.9

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY Pipfile Pipfile.lock /app/

# Install pipenv and install dependencies
RUN pip install pipenv
RUN pipenv --python /usr/local/bin/python3
RUN pipenv install --deploy --ignore-pipfile

# Copy the application code into the container
COPY . /app/

# Command to run the Flask app
CMD ["pipenv", "run", "python", "app.py"]