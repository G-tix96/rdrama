FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt update
RUN apt -y upgrade
RUN apt install -y supervisor 
RUN apt install -y python3-pip
RUN apt install -y ffmpeg
RUN apt install -y imagemagick
RUN apt install -y postgresql
RUN apt install -y libpq-dev
RUN apt install -y nano
RUN apt install -y exiv2

COPY requirements.txt /etc/requirements.txt

RUN pip3 install -r /etc/requirements.txt

RUN mkdir /images
RUN mkdir /songs
RUN mkdir /videos
RUN mkdir /audio
RUN mkdir /asset_submissions
RUN mkdir /asset_submissions/marseys
RUN mkdir /asset_submissions/hats
RUN mkdir /asset_submissions/marseys/original
RUN mkdir /asset_submissions/hats/original
RUN mkdir /var/log/rdrama

RUN chown rdrama:rdrama /var/log/rdrama

ENV NODE_VERSION=16.13.0
RUN apt install -y curl
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
ENV NVM_DIRECTORY=/root/.nvm
RUN . "$NVM_DIRECTORY/nvm.sh" && nvm install ${NODE_VERSION}
RUN . "$NVM_DIRECTORY/nvm.sh" && nvm use v${NODE_VERSION}
RUN . "$NVM_DIRECTORY/nvm.sh" && nvm alias default v${NODE_VERSION}
ENV PATH="/root/.nvm/versions/node/v${NODE_VERSION}/bin/:${PATH}"
RUN node --version
RUN npm --version
RUN npm i -g yarn

RUN apt install -y nginx
RUN rm /etc/nginx/sites-available -r
RUN rm /etc/nginx/sites-enabled/default
RUN mkdir /etc/nginx/includes

# Note: production uses ImageMagick 7.1, whereas 22.04 repos have 6.9.
# TODO: imei.sh broken: "Signature verification failed!" Workaround pending fix.
#COPY imei.sh /opt/imei.sh
#RUN bash /opt/imei.sh
RUN ln -s /usr/bin/convert /usr/local/bin/magick

EXPOSE 80/tcp

CMD [ "/usr/bin/supervisord", "-c", "/rDrama/supervisord.conf" ]
