# AWM

## Overview

Implements EOSC Application Workflow Management API.

## Requirements

Python 3.5.2+

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
