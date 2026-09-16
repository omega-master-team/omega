FROM debian:12-slim

RUN apt-get update \
	&& apt-get upgrade -y \
	&& apt-get install -y php-cli libzip-dev php-mysql php-curl \
	&& apt-get clean

WORKDIR /app

CMD php -S 0.0.0.0:9000 -t public
