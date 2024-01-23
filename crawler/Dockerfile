FROM ubuntu

# Changes working directory to `/app` within docker image
WORKDIR /app

# Installs python3
RUN apt update && \
    apt install -y wget python3 openjdk-11-jre

# Copies everything in the local folder `./crawler/` into the container folder `/app`
COPY . . 

RUN wget https://repo1.maven.org/maven2/org/archive/heritrix/heritrix/3.4.0-20220727/heritrix-3.4.0-20220727-dist.tar.gz -O src/heritrix-3.4.0-20220727-dist.tar.gz
RUN tar xzvf src/heritrix-3.4.0-20220727-dist.tar.gz
RUN ln -s heritrix-3.4.0-20220727 heritrix
RUN echo "admin:p4ssw0rd" > auth.conf
RUN cp src/warcfilter-1.0-SNAPSHOT.jar heritrix/lib

CMD ["bash", "./src/start_crawl_job.sh"]
