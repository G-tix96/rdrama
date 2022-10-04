FROM ubuntu:22.04

ADD .. /service

RUN /service/ubuntu_setup.sh

EXPOSE 80/tcp

RUN apt install -y supervisor

CMD [ "/usr/bin/supervisord", "-c", "/service/supervisord.conf" ]
