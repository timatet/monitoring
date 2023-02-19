FROM python:3.8-slim

WORKDIR /app
# Installing the necessary linux packages
RUN apt update && \
    apt install -y curl iputils-ping curl
# Copying and installing dependencies 
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY ./data/config_example.yml config.yml
# Copying and running the script itself
COPY monitoring.py monitoring.py
CMD [ "python3", "monitoring.py"]