FROM ubuntu:22.04

ENV PIP_CACHE_DIR=/var/cache/buildkit/pip
RUN mkdir -p $PIP_CACHE_DIR
RUN rm -f /etc/apt/apt.conf.d/docker-clean
RUN --mount=type=cache,target=/var/cache/apt \
	apt-get update && apt-get install -yqq --no-install-recommends \
	python3 python3-pip && rm -rf /var/lib/apt/lists/*


# Changes working directory to `/app` within docker image
WORKDIR /app

COPY requirements.txt .

RUN --mount=type=cache,target=$PIP_CACHE_DIR python3 -m pip install --cache-dir $PIP_CACHE_DIR -r requirements.txt

# Copies everything in the local folder `./dblp-export/` into the container folder `/app`
COPY . . 

CMD ["python3", "./src/dblp-revelant-hosts.py"]
