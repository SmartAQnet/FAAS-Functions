FROM python:3.7.4-slim-buster
RUN apt-get update && apt-get install wget libyajl-dev pkg-config gcc g++ -y
COPY . /app
WORKDIR /app
RUN pip install pipenv
RUN pipenv install
ENTRYPOINT ["pipenv", "run"]