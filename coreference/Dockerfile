FROM ubuntu:22.04

ENV PIP_CACHE_DIR=/var/cache/buildkit/pip
RUN mkdir -p $PIP_CACHE_DIR
RUN rm -f /etc/apt/apt.conf.d/docker-clean
RUN --mount=type=cache,target=/var/cache/apt \
	apt-get update && apt-get install -yqq --no-install-recommends \
	python3 python3-pip git && rm -rf /var/lib/apt/lists/*

# Changes working directory to `/app` within docker image
WORKDIR /app
# VOLUME /app

# RUN git clone  --depth=1 git://github.com/pyenv/pyenv.git .pyenv
# ENV PYENV_ROOT /app/.pyenv
# ENV PATH $PYENV_ROOT/shims:/$PYENV_ROOT/bin:$PATH


# manage python virtual environment
# RUN pyenv install 3.10.6

# Install dependencies:
COPY requirements.txt .
RUN python3 -m pip install --cache-dir $PIP_CACHE_DIR -r requirements.txt

# download spacy model 
RUN python3 -m spacy download en_core_web_md

# Copies everything in the local folder `./coreference/` into the container folder `/app`
COPY . . 

CMD ["bash", "./src/run.sh"]
