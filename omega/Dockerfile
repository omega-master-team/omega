FROM debian:bullseye-slim

# Install omega dependencies
RUN \
	apt-get update \
	&& apt-get upgrade -y \
	&& apt-get install -y python3 python3-pip \
	&& pip3 install discord.py requests requests_oauthlib mysql-connector-python \
	&& apt-get clean

WORKDIR /app
