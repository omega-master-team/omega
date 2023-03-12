FROM debian:bullseye-slim

# Install omega dependencies
RUN \
    apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y python3 python3-pip \
    && pip3 install discord requests requests_oauthlib \
    && apt-get clean

# Install rust dep
RUN \
    apt-get update \
    && apt-get install -y curl \
    && (curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y) \
    && apt-get purge -y curl \
    && apt-get autoremove -y \
    && apt-get clean

WORKDIR /app

# Copy sources
COPY ../../omega.py .
COPY ../../oauth/ oauth/

# Build sources
RUN \
    apt-get update \
    && apt-get install -y pkg-config libssl-dev libsqlite3-dev \
    && cd oauth && ~/.cargo/bin/cargo build --release && cd .. \
    && apt-get clean

# Create cert folder
RUN mkdir -p cert

# Runtime
COPY entrypoint.sh .
ENTRYPOINT [ "bash", "entrypoint.sh" ]
