#!/bin/bash

cd oauth && ~/.cargo/bin/cargo build --release
env DB_FILE=/app/omega.db /app/oauth/target/release/oauth
