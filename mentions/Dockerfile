FROM ubuntu

# Changes working directory to `/app` within docker image
WORKDIR /app

# Installs python3
RUN apt update && \
    apt install -y python3

#install get
RUN apt-get update && apt-get install -y python3-pip

COPY requirements.txt .

RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY src/config.yaml .
COPY src/grobid_client_python/ ./grobid_client_python

# Copies everything in the local folder `./mentions/` into the container folder `/app`
COPY . .

#RUN mkdir /data/mentions/in_pdfs  /data/mentions/out_tei /data/mentions/results
#RUN cp src/resources/data/  /data/mentions/

CMD ["python3", "./src/main.py"]
