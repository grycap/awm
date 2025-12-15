# AWM

## Overview

Implements EOSC Application Workflow Management API.

## Requirements

Python 3.5.2+

## Configuration

Set this environment variables to configure the AWM service:

```bash
LOG_LEVEL=info
DB_URL=file:///tmp/awm.db
IM_URL=http://localhost:8800
ALLOCATION_STORE="db" # or vault
VAULT_URL=https://secrets.egi.eu
```

Or you can set an `.env` file as the `.env.example` provided.

## Usage

To run the server, please execute the following from the root directory:

```bash
pip3 install -r requirements.txt
python3 -m awm
```

and open your browser to here:

```bash
http://localhost:8080/
```

## Running with Docker

To run the server on a Docker container, please execute the following from the root directory:

```bash
# building the image
docker build -t awm .

# starting up a container
docker run -p 8080:8080 awm
```
