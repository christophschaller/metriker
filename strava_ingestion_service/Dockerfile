#FROM python:3.9

#ADD strava_ingestion_service .

#RUN pip install logging sentry_sdk FastAPI

#CMD ["python","./strava_ingestion_service/main.py"]

# Start with the official Python 3.9 image
FROM python:3.9

# Set the working directory in the Docker image
WORKDIR /app

# Copy the Poetry files to the working directory in the Docker image
#COPY ./strava_ingestion_service/pyproject.toml /app/pyproject.toml
COPY ./database_utils /app/database_utils
COPY ./strava_ingestion_service/pyproject.toml ./strava_ingestion_service/poetry.lock* /app/

# Install Poetry
RUN pip install poetry

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes --without dev
RUN pip install --no-cache-dir -r requirements.txt

# Install project dependencies using Poetry
# RUN poetry install --no-root --only main

# Copy the rest of the application code to the working directory in the Docker image
COPY ./strava_ingestion_service/strava_ingestion_service /app

# Set the command to run the application
CMD [ "python", "./main.py" ]
