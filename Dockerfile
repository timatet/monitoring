FROM python:3.8-slim

WORKDIR /app
# Installing the necessary linux packages
RUN apt update && \
    apt install -y iputils-ping curl locales locales-all
# EN language pack for OS
ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8
RUN locale-gen en_US.UTF-8 && dpkg-reconfigure locales
# Copying and installing dependencies 
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY ./data/config_example.yml config.yml
# Copying and running the script itself
COPY *.py ./
CMD [ "python3", "monitoring.py"]