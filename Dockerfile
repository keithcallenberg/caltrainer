FROM python:2
ENV PYTHONUNBUFFERED 1

ADD requirements.txt /
RUN pip install -r /requirements.txt
ADD ./src/ /code
WORKDIR /code

RUN echo "TERM=xterm; export TERM" >> /etc/bash.bashrc

RUN chmod a+x /code/entrypoint.sh