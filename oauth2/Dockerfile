FROM debian:bullseye-slim

RUN \
    apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y php-cli libzip-dev php-mysql \
    && apt-get clean

WORKDIR /app

CMD php -S 0.0.0.0:9000 -t public
