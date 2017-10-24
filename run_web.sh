#!/usr/bin/env bash

#judgement
if [[ -a /etc/supervisor/conf.d/supervisord.conf ]]; then
  exit 0
fi

# generate documentation (temporarily disabled)
#/make_docs.sh

# run migrate for any new migrations
python manage.py migrate --noinput

# run django collectstatic before we start the server
#python manage.py collectstatic --noinput

#supervisor
cat > /etc/supervisor/conf.d/supervisord.conf <<EOF
[supervisord]
nodaemon=true

[program:rsyslog]
command=/usr/sbin/rsyslogd -n

[program:django]
command=uwsgi --ini uwsgi.ini $1

[program:prepare_static]
command=python manage.py collectstatic --noinput
exitcodes=0
autorestart=false
startsecs=0
EOF