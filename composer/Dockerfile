FROM debian:bullseye-slim

RUN \
    apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y php-cli libzip-dev php-mysql php-curl php-zip git \
    && apt-get clean

RUN php -r "copy('https://getcomposer.org/installer', 'composer-setup.php');" \
    && php composer-setup.php \
    && php -r "unlink('composer-setup.php');" \
    && mv composer.phar /bin/composer

WORKDIR /app

CMD composer u -W
