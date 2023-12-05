FROM techblog/techblog/flask

LABEL maintainer="tomer.klein@gmail.com"

ENV PYTHONIOENCODING=utf-8

#install pip3
RUN apt update -yqq && \
    apt install -yqq && \
    apt install python3-pip -yqq && \
    apt install libffi-dev -yqq && \
    apt install libssl-dev -yqq && \
    apt install dsniff -yqq

#Create working directory
RUN mkdir /opt/arpspoof

EXPOSE 7022

COPY arpspoof /opt/arpspoof

ENTRYPOINT ["/usr/bin/python3", "/opt/arpspoof/arpspoof.py"]
