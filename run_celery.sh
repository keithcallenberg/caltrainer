#!/usr/bin/env bash

CONCURRENCY=$1

# clean-up
if [[ -a /tmp/celerybeat.pid ]]; then
  rm /tmp/celerybeat.pid
fi

if [[ -a /etc/supervisor/conf.d/supervisord.conf ]]; then
  exit 0
fi

#supervisor
cat > /etc/supervisor/conf.d/supervisord.conf <<EOF
[supervisord]
nodaemon=true
#loglevel=debug

[program:rsyslog]
command=/usr/sbin/rsyslogd -n
EOF
