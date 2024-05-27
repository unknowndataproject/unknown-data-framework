#FROM ubuntu:22.04 as base
# Use the NVIDIA base image for Ubuntu 22.04 and your architecture
FROM nvcr.io/nvidia/cuda:12.4.0-devel-ubuntu22.04

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

CMD ["python3", "./src/main_mentions-pdf.py"]
