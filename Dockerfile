FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive

RUN apt update
RUN apt -y upgrade
RUN apt install -y supervisor
RUN apt install -y python3-pip
RUN apt install -y ffmpeg
RUN apt install -y postgresql
RUN apt install -y libpq-dev
RUN apt install -y nano

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

RUN apt install -y nginx
RUN rm /etc/nginx/sites-available -r
RUN rm /etc/nginx/sites-enabled/default
RUN mkdir /etc/nginx/includes

COPY imei.sh /opt/imei.sh
RUN bash /opt/imei.sh

EXPOSE 80/tcp

CMD [ "/usr/bin/supervisord", "-c", "/rDrama/supervisord.conf" ]
