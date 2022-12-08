# Build this container from parent directory, specifying path to this file

FROM python:3.9-slim

RUN apt-get update
RUN apt-get -y install gcc

RUN mkdir /app
COPY ./tests/requirements.txt /app/tests/requirements.txt

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r /app/tests/requirements.txt

# in production ./toppings.json must be delivered by student
COPY . /app/
