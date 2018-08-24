FROM python:2.7

RUN mkdir -p /usr/local/app
ADD . /usr/local/app

WORKDIR /usr/local/app

RUN pip install -r requirements.txt

EXPOSE 5000