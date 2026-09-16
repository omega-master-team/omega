FROM debian:12-slim

RUN apt-get update \
	&& apt-get upgrade -y \
	&& apt-get install -y python3 python3-pip \
	&& apt-get clean

RUN	pip3 install discord.py requests requests_oauthlib mysql-connector-python --break-system-packages

WORKDIR /app
