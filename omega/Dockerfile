FROM debian:bullseye-slim

# Install omega dependencies
RUN \
    apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y python3 python3-pip \
    && pip3 install discord.py requests requests_oauthlib \
    && apt-get clean

WORKDIR /app

# Copy sources
COPY omega.py .

# Runtime
CMD python3 omega.py