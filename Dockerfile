FROM ubuntu:18.04

LABEL maintainer="tomer.klein@gmail.com"

ENV PYTHONIOENCODING=utf-8

#install pip3
RUN apt update -yqq && \
    apt install -yqq && \
    apt install python3-pip -yqq && \
    apt install libffi-dev -yqq && \
    apt install libssl-dev -yqq && \
    apt install dsniff -yqq

RUN  pip3 install --upgrade pip --no-cache-dir && \
     pip3 install --upgrade setuptools --no-cache-dir && \
     pip3 install flask  --no-cache-dir && \
     pip3 install flask_restful  --no-cache-dir && \
     pip3 install loguru  --no-cache-dir && \
     pip3 install cryptography==2.6.1 --no-cache-dir


#Create working directory
RUN mkdir /opt/arpspoof

EXPOSE 7022

COPY arpspoof /opt/arpspoof

ENTRYPOINT ["/usr/bin/python3", "/opt/arpspoof/arpspoof.py"]
