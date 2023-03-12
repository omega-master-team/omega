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

# Copy sources
COPY . oauth/

# Build sources
RUN cd oauth && ~/.cargo/bin/cargo build --release

# Runtime
CMD env DB_FILE=/app/omega.db /app/oauth/target/release/oauth
