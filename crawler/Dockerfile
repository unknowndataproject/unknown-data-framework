FROM ubuntu:22.04

ENV PIP_CACHE_DIR=/var/cache/buildkit/pip
RUN mkdir -p $PIP_CACHE_DIR
RUN rm -f /etc/apt/apt.conf.d/docker-clean
RUN --mount=type=cache,target=/var/cache/apt \
	apt-get update && apt-get install -yqq --no-install-recommends \
	wget python3 openjdk-11-jre && rm -rf /var/lib/apt/lists/*

# Changes working directory to `/app` within docker image
WORKDIR /app

# Copies everything in the local folder `./crawler/` into the container folder `/app`
COPY . . 

RUN wget https://repo1.maven.org/maven2/org/archive/heritrix/heritrix/3.4.0-20220727/heritrix-3.4.0-20220727-dist.tar.gz -O src/heritrix-3.4.0-20220727-dist.tar.gz
RUN tar xzvf src/heritrix-3.4.0-20220727-dist.tar.gz
RUN ln -s heritrix-3.4.0-20220727 heritrix
RUN echo "admin:p4ssw0rd" > auth.conf
RUN cp src/warcfilter-1.1-SNAPSHOT.jar heritrix/lib

CMD ["bash", "./src/start_crawl_job.sh"]
