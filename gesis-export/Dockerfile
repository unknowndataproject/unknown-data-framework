# Use the NVIDIA base image for Ubuntu 22.04 and your architecture
FROM nvcr.io/nvidia/cuda:12.4.0-devel-ubuntu22.04

# Changes working directory to `/app` within docker image
WORKDIR /app

# Installs python3
RUN apt update && \
    apt install -y python3

# Copies everything in the local folder `./gesis-export/` into the container folder `/app`
COPY . . 

CMD ["python3", "./src/hello.py"]