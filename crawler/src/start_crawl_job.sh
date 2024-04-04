#!/bin/bash


# create crawl job

mkdir -p /data/crawler/test_job/
ln -s /data/crawler/test_job /app/heritrix/jobs/test_job
cp /app/src/crawler-beans.cxml /app/src/seeds.txt /app/heritrix/jobs/test_job

# start heritrix crawler

HERITRIX_HOME=/app/heritrix JAVA_OPTS=-Xmx8192M FOREGROUND=true /app/heritrix/bin/heritrix --web-admin @/app/auth.conf --web-bind-hosts 0.0.0.0 --web-port 8443 --run-job "test_job"
