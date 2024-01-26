FROM ubuntu

# Changes working directory to `/app` within docker image
WORKDIR /app
# VOLUME /app

# Installs python3
RUN apt update && \
    apt install -y git 
    
RUN apt install -y python3 
RUN apt install -y python3-pip
# RUN git clone  --depth=1 git://github.com/pyenv/pyenv.git .pyenv
# ENV PYENV_ROOT /app/.pyenv
# ENV PATH $PYENV_ROOT/shims:/$PYENV_ROOT/bin:$PATH


# manage python virtual environment
# RUN pyenv install 3.10.6

# Install dependencies:
COPY requirements.txt .
RUN pip install -r requirements.txt

# download spacy model 
RUN python3 -m spacy download en_core_web_md

# Copies everything in the local folder `./coreference/` into the container folder `/app`
COPY . . 

CMD ["python3", "./src/test_run_linking.py"]
