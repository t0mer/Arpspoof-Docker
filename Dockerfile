FROM ubuntu:18.04

LABEL maintainer="tomer.klein@gmail.com"

ENV PYTHONIOENCODING=utf-8

#install pip3
RUN apt update

RUN apt install python3-pip libffi-dev libssl-dev dsniff --yes
RUN pip3 install flask flask_restful loguru cryptography==2.6.1 --no-cache-dir

#Create working directory
RUN mkdir /opt/arpspoof

EXPOSE 7022

COPY arpspoof /opt/arpspoof

ENTRYPOINT ["/usr/bin/python3", "/opt/arpspoof/arpspoof.py"]