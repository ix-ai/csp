# csp

[![Pipeline Status](https://gitlab.com/ix.ai/csp/badges/master/pipeline.svg)](https://gitlab.com/ix.ai/csp/)
[![Docker Stars](https://img.shields.io/docker/stars/ixdotai/csp.svg)](https://hub.docker.com/r/ixdotai/csp/)
[![Docker Pulls](https://img.shields.io/docker/pulls/ixdotai/csp.svg)](https://hub.docker.com/r/ixdotai/csp/)
[![Gitlab Project](https://img.shields.io/badge/GitLab-Project-554488.svg)](https://gitlab.com/ix.ai/csp/)

A basic Content Security Policy processor running in docker

## WIP Warning
This is still work in progress

## What does it do?
It logs to STDOUT (and, optionally, to a GELF capable host) the received HTTP POST request.

The request has to go to the path `/csp`.

Just add the header:
```
Content-Security-Policy-Report-Only: upgrade-insecure-requests; default-src 'self'; report-uri https://example.com/csp;
```

## Usage Examples

### CLI
```sh
docker run --rm -it \
    -p 9999:80 \
    -e PORT=80 \
    -e GELF_HOST=graylog \
    --name csp \
    ixdotai/csp:latest
```

### docker-compose
```yml
version: "3.7"

services:
  csp:
    image: ixdotai/csp:latest
    environment:
      PORT: '80'
    ports:
      - '9999:80'
```

### docker stack with traefik
```
version: "3.7"

services:
  csp:
    image: ixdotai/csp:latest
    deploy:
      labels:
        traefik.enable: 'true'
        traefik.http.routers.csp.entrypoints: http,https
        traefik.http.routers.csp.service: csp@docker
        traefik.http.routers.csp.rule: "Host(`csp.example.com`)"
        traefik.http.routers.csp.tls.certResolver: 'default'
        traefik.http.services.csp.loadbalancer.server.port: '9180'
[...]
  my-website:
    deploy:
      labels:
[...]
        traefik.http.middlewares.website-csp.headers.customResponseHeaders.Content-Security-Policy-Report-Only: "upgrade-insecure-requests; default-src 'self' https://cdnjs.cloudflare.com; script-src 'self' https://cdnjs.cloudflare.com https://s.ytimg.com; font-src https://fonts.gstatic.com https://cdnjs.cloudflare.com; report-uri https://csp.example.com/csp;"
        traefik.http.routers.website.middlewares: website-csp
[...]

```

### Environment

| **Variable**         | **Default** | **Description**                                                        |
|:---------------------|:-----------:|:-----------------------------------------------------------------------|
| `MAX_CONTENT_LENGTH` | `4096`      | The maximum content length of the HTTP POST                            |
| `LOGLEVEL`           | `INFO`      | [Logging Level](https://docs.python.org/3/library/logging.html#levels) |
| `GELF_HOST`          | -           | If set, GELF UDP logging to this host will be enabled                  |
| `GELF_PORT`          | `12201`     | Ignored, if `GELF_HOST` is unset. The UDP port for GELF logging        |
| `PORT`               | `9180`      | The port to bind to                                                    |
| `ADDRESS`            | `*`         | The IP address to bind to                                              |

## Resources:
* GitLab: https://gitlab.com/ix.ai/csp
* Docker Hub: https://hub.docker.com/r/ixdotai/csp
