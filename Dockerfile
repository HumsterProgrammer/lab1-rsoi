FROM python:3.11-slim


#RUN apt-get update -m
RUN apt-get update && apt-get install -y libpq-dev gcc

# set a directory for the app
WORKDIR /usr/src/app

# copy requirements file and install dependencies (for optimal layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy all remaining files to the container
COPY ./src .

# tell the port number the container should expose
EXPOSE 5000

RUN python -c "import psycopg2; print(f'psycopg2 libpq version: {psycopg2.__libpq_version__}'); print(1)"

# run the command
CMD ["python", "./app.py"]
