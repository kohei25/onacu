FROM python:3.6
ENV PYTHONUNBUFFERED 1
RUN mkdir /onacu
WORKDIR /onacu
COPY requirements.txt /onacu/
RUN pip install -r requirements.txt
COPY . /onacu/