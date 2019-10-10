# csp

A basic Content Security Policy processor running in docker

## WIP Warning
This is still work in progress

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
    image: ixdotai/csp
    environment:
      PORT: '80'
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
