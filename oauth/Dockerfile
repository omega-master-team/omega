FROM debian:bullseye-slim

# Install rust dep
RUN \
    apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y curl pkg-config libssl-dev libsqlite3-dev gcc \
    && (curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y) \
    && apt-get purge -y curl \
    && apt-get autoremove -y \
    && apt-get clean

WORKDIR /app
RUN mkdir -p /app/cert

VOLUME /app/oauth

COPY entrypoint.sh /app/entrypoint.sh
ENTRYPOINT bash entrypoint.sh
