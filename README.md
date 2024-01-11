# UnknownData Framework


## Requirements 
* Docker. The simples way to install docker is to install [Docker Desktop](https://docs.docker.com/desktop/)

## How to Run
The following paragraph explains how to run the software components using docker compose. The flag `--build` is used in each command to ensure the created docker container are being rebuild and thu use the latest available source code.

### Whole Pipeline
If you want to run the whole pipeline, use the following command from within the project root folder:

```bash
docker compose up --build
```

That command will run all components in the order `crawler` -> `mentions` -> `coreference` -> `dblp-export`. Each component will only start to run when the previous one finished successfully. 

### Only One Component
If you only want to run one component of the pipeline, use the following command from within the project root folder and replace `[COMPONENT]` by the desired component name (`crawler`, `mentions`, `coreference`, `dblp-export`):

```bash
docker compose up [COMPONENT] --build
```

## Development
For each software component there is one folder and one Dockerfile that defines a docker image. 

Feel free to adapt the folder stucture and the Dockerfile of your software component as needed. 

Please adapt the README.md file of your software component for a light documentation of you component.