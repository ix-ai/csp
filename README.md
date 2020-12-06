# csp

[![Pipeline Status](https://gitlab.com/ix.ai/csp/badges/master/pipeline.svg)](https://gitlab.com/ix.ai/csp/)
[![Docker Stars](https://img.shields.io/docker/stars/ixdotai/csp.svg)](https://hub.docker.com/r/ixdotai/csp/)
[![Docker Pulls](https://img.shields.io/docker/pulls/ixdotai/csp.svg)](https://hub.docker.com/r/ixdotai/csp/)
[![Gitlab Project](https://img.shields.io/badge/GitLab-Project-554488.svg)](https://gitlab.com/ix.ai/csp/)

A basic Content Security Policy processor running in docker

## WIP Warning
This is still work in progress

## What does it do?
It logs to STDOUT (LOGLEVEL `INFO`) and, optionally, to a GELF capable host, the received CSP violation.

The request must go to the path `/csp` (default) or to the path set in the environment variable `CSP_PATH`.

Just add the header:
```
Content-Security-Policy-Report-Only: upgrade-insecure-requests; default-src 'self'; report-uri https://example.com/csp;
```

### Invalid requests
The following requests are not logged at all, instead a warning is logged:
* Zero-length requests (a HTTP POST containing no payload)
* Requests larger than `MAX_CONTENT_LENGTH`

All other requests log the underlying WSGI environment to log level `DEBUG`. Non-JSON requests are also logged to the same level.

## Healthcheck
To enable a healthcheck, just point it to `/healthz` (default) or to the value set for the environment variable `HEALTHZ_PATH`. You can use `ENABLE_HEALTHZ_VERSION` to also have CSP display the version and build information (disabled by default).

## Usage Examples

### CLI
```sh
docker run --rm -it \
    -p 9999:80 \
    -e PORT=80 \
    -e GELF_HOST=graylog \
    --name csp \
    registry.gitlab.com/ix.ai/csp:latest
```

### docker-compose
```yml
version: "3.7"

services:
  csp:
    image: registry.gitlab.com/ix.ai/csp:latest
    environment:
      PORT: '80'
      MAX_CONTENT_LENGTH: '512'
    ports:
      - '9999:80'
```

### docker stack with traefik
```yml
version: "3.7"

services:
  csp:
    image: registry.gitlab.com/ix.ai/csp:latest
    deploy:
      labels:
        traefik.enable: 'true'
        traefik.http.routers.csp.entrypoints: http,https
        traefik.http.routers.csp.rule: "Host(`csp.example.com`) && Path(`/`)"
        traefik.http.routers.csp.tls.certResolver: 'default'
        traefik.http.routers.csp-metrics.entrypoints: http,https
        traefik.http.routers.csp-metrics.rule: "Host(`csp.example.com`) && Path(`/metrics`)"
        traefik.http.routers.csp-metrics.middlewares: auth
        traefik.http.routers.csp-metrics.tls.certResolver: 'default'
        traefik.http.services.csp.loadbalancer.server.port: '9180'
    environment:
      CSP_PATH: '/'
      HEALTHZ_PATH: '/health'
      ENABLE_METRICS: 'yes'
[...]
  my-website:
    deploy:
      labels:
        traefik.http.middlewares.website-csp.headers.customResponseHeaders.Content-Security-Policy-Report-Only: "upgrade-insecure-requests; default-src 'self' https://cdnjs.cloudflare.com; script-src 'self' https://cdnjs.cloudflare.com https://s.ytimg.com; font-src https://fonts.gstatic.com https://cdnjs.cloudflare.com; report-uri https://csp.example.com/;"
        traefik.http.routers.website.middlewares: website-csp
[...]

```

## Output example
Firefox browser and `LOGLEVEL: INFO`
```
2020-12-06 14:25:42.853 WARNING [__main__.<module>] Starting **csp refactor-225909200**. Listening on *:9180
2020-12-06 14:28:15.442 INFO [csp.log_csp] {"csp-report": {"blocked-uri": "inline", "document-uri": "https://xxxREDACTEDxxx/", "original-policy": "upgrade-insecure-requests; default-src 'self' https://cdnjs.cloudflare.com; script-src 'self' https://cdnjs.cloudflare.com https://s.ytimg.com; font-src https://fonts.gstatic.com https://cdnjs.cloudflare.com; report-uri https://csp.example.com/csp", "referrer": "", "source-file": "https://xxxREDACTEDxxx/", "violated-directive": "default-src"}}
2020-12-06 14:28:15.711 INFO [csp.log_csp] {"csp-report": {"blocked-uri": "inline", "column-number": 1, "document-uri": "https://xxxREDACTEDxxx/", "line-number": 925, "original-policy": "upgrade-insecure-requests; default-src 'self' https://cdnjs.cloudflare.com; script-src 'self' https://cdnjs.cloudflare.com https://s.ytimg.com; font-src https://fonts.gstatic.com https://cdnjs.cloudflare.com; report-uri https://csp.example.com/csp", "referrer": "", "source-file": "https://xxxREDACTEDxxx/", "violated-directive": "script-src"}}
2020-12-06 14:28:15.724 INFO [csp.log_csp] {"csp-report": {"blocked-uri": "inline", "column-number": 3975, "document-uri": "https://xxxREDACTEDxxx/", "line-number": 3, "original-policy": "upgrade-insecure-requests; default-src 'self' https://cdnjs.cloudflare.com; script-src 'self' https://cdnjs.cloudflare.com https://s.ytimg.com; font-src https://fonts.gstatic.com https://cdnjs.cloudflare.com; report-uri https://csp.example.com/csp", "referrer": "", "source-file": "https://cdnjs.cloudflare.com/ajax/libs/jquery/2.2.4/jquery.min.js", "violated-directive": "default-src"}}
2020-12-06 14:28:15.735 INFO [csp.log_csp] {"csp-report": {"blocked-uri": "inline", "column-number": 3975, "document-uri": "https://xxxREDACTEDxxx/", "line-number": 3, "original-policy": "upgrade-insecure-requests; default-src 'self' https://cdnjs.cloudflare.com; script-src 'self' https://cdnjs.cloudflare.com https://s.ytimg.com; font-src https://fonts.gstatic.com https://cdnjs.cloudflare.com; report-uri https://csp.example.com/csp", "referrer": "", "source-file": "https://cdnjs.cloudflare.com/ajax/libs/jquery/2.2.4/jquery.min.js", "violated-directive": "default-src"}}
2020-12-06 14:28:15.738 INFO [csp.log_csp] {"csp-report": {"blocked-uri": "inline", "column-number": 14648, "document-uri": "https://xxxREDACTEDxxx/", "line-number": 3, "original-policy": "upgrade-insecure-requests; default-src 'self' https://cdnjs.cloudflare.com; script-src 'self' https://cdnjs.cloudflare.com https://s.ytimg.com; font-src https://fonts.gstatic.com https://cdnjs.cloudflare.com; report-uri https://csp.example.com/csp", "referrer": "", "source-file": "https://cdnjs.cloudflare.com/ajax/libs/jquery/2.2.4/jquery.min.js", "violated-directive": "default-src"}}
```
Google Chrome browser and `LOGLEVEL: DEBUG`
```
2020-12-06 14:38:27.132 DEBUG [csp.log_csp] {'REMOTE_ADDR': '10.0.14.14', 'REMOTE_HOST': '10.0.14.14', 'REMOTE_PORT': '56224', 'REQUEST_METHOD': 'POST', 'SERVER_PORT': '9180', 'SERVER_NAME': '9f02bb970b0b', 'SERVER_SOFTWARE': None, 'SERVER_PROTOCOL': 'HTTP/1.1', 'SCRIPT_NAME': '', 'PATH_INFO': '/csp', 'QUERY_STRING': '', 'wsgi.url_scheme': 'http', 'wsgi.version': (1, 0), 'wsgi.errors': <_io.TextIOWrapper name='<stderr>' mode='w' encoding='utf-8'>, 'wsgi.multithread': True, 'wsgi.multiprocess': False, 'wsgi.run_once': False, 'wsgi.input': <_io.BytesIO object at 0x7fb398c89720>, 'wsgi.file_wrapper': <class 'waitress.buffers.ReadOnlyFileBasedBuffer'>, 'wsgi.input_terminated': True, 'HTTP_HOST': 'csp.example.com', 'HTTP_USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36', 'CONTENT_LENGTH': '548', 'HTTP_ACCEPT': '*/*', 'HTTP_ACCEPT_ENCODING': 'gzip, deflate, br', 'HTTP_ACCEPT_LANGUAGE': 'en-DE,en-GB;q=0.9,en;q=0.8,de-DE;q=0.7,de;q=0.6,ro-RO;q=0.5,ro;q=0.4,en-US;q=0.3', 'CONTENT_TYPE': 'application/csp-report', 'HTTP_DNT': '1', 'HTTP_ORIGIN': 'https://xxxREDACTEDxxx', 'HTTP_REFERER': 'https://xxxREDACTEDxxx/', 'HTTP_SEC_FETCH_DEST': 'report', 'HTTP_SEC_FETCH_MODE': 'no-cors', 'HTTP_SEC_FETCH_SITE': 'cross-site', 'HTTP_X_FORWARDED_FOR': '2001:0DB8::1', 'HTTP_X_FORWARDED_HOST': 'csp.example.com', 'HTTP_X_FORWARDED_PORT': '443', 'HTTP_X_FORWARDED_PROTO': 'https', 'HTTP_X_FORWARDED_SERVER': '2319d1b2d5bf', 'HTTP_X_REAL_IP': '2001:0DB8::1', 'werkzeug.request': <Request 'http://csp.example.com/csp' [POST]>}
2020-12-06 14:38:27.132 INFO [csp.log_csp] {"csp-report": {"document-uri": "https://xxxREDACTEDxxx/", "referrer": "", "violated-directive": "script-src-elem", "effective-directive": "script-src-elem", "original-policy": "upgrade-insecure-requests; default-src 'self' https://cdnjs.cloudflare.com; script-src 'self' https://cdnjs.cloudflare.com https://s.ytimg.com; font-src https://fonts.gstatic.com https://cdnjs.cloudflare.com; report-uri https://csp.example.com/csp;", "disposition": "report", "blocked-uri": "inline", "line-number": 925, "source-file": "https://xxxREDACTEDxxx/", "status-code": 0, "script-sample": ""}}
2020-12-06 14:38:27.134 DEBUG [csp.log_csp] {'REMOTE_ADDR': '10.0.14.14', 'REMOTE_HOST': '10.0.14.14', 'REMOTE_PORT': '56220', 'REQUEST_METHOD': 'POST', 'SERVER_PORT': '9180', 'SERVER_NAME': '9f02bb970b0b', 'SERVER_SOFTWARE': None, 'SERVER_PROTOCOL': 'HTTP/1.1', 'SCRIPT_NAME': '', 'PATH_INFO': '/csp', 'QUERY_STRING': '', 'wsgi.url_scheme': 'http', 'wsgi.version': (1, 0), 'wsgi.errors': <_io.TextIOWrapper name='<stderr>' mode='w' encoding='utf-8'>, 'wsgi.multithread': True, 'wsgi.multiprocess': False, 'wsgi.run_once': False, 'wsgi.input': <_io.BytesIO object at 0x7fb398c89720>, 'wsgi.file_wrapper': <class 'waitress.buffers.ReadOnlyFileBasedBuffer'>, 'wsgi.input_terminated': True, 'HTTP_HOST': 'csp.example.com', 'HTTP_USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36', 'CONTENT_LENGTH': '609', 'HTTP_ACCEPT': '*/*', 'HTTP_ACCEPT_ENCODING': 'gzip, deflate, br', 'HTTP_ACCEPT_LANGUAGE': 'en-DE,en-GB;q=0.9,en;q=0.8,de-DE;q=0.7,de;q=0.6,ro-RO;q=0.5,ro;q=0.4,en-US;q=0.3', 'CONTENT_TYPE': 'application/csp-report', 'HTTP_DNT': '1', 'HTTP_ORIGIN': 'https://xxxREDACTEDxxx', 'HTTP_REFERER': 'https://xxxREDACTEDxxx/', 'HTTP_SEC_FETCH_DEST': 'report', 'HTTP_SEC_FETCH_MODE': 'no-cors', 'HTTP_SEC_FETCH_SITE': 'cross-site', 'HTTP_X_FORWARDED_FOR': '2001:0DB8::1', 'HTTP_X_FORWARDED_HOST': 'csp.example.com', 'HTTP_X_FORWARDED_PORT': '443', 'HTTP_X_FORWARDED_PROTO': 'https', 'HTTP_X_FORWARDED_SERVER': '2319d1b2d5bf', 'HTTP_X_REAL_IP': '2001:0DB8::1', 'werkzeug.request': <Request 'http://csp.example.com/csp' [POST]>}
2020-12-06 14:38:27.134 DEBUG [csp.log_csp] {'REMOTE_ADDR': '10.0.14.14', 'REMOTE_HOST': '10.0.14.14', 'REMOTE_PORT': '56222', 'REQUEST_METHOD': 'POST', 'SERVER_PORT': '9180', 'SERVER_NAME': '9f02bb970b0b', 'SERVER_SOFTWARE': None, 'SERVER_PROTOCOL': 'HTTP/1.1', 'SCRIPT_NAME': '', 'PATH_INFO': '/csp', 'QUERY_STRING': '', 'wsgi.url_scheme': 'http', 'wsgi.version': (1, 0), 'wsgi.errors': <_io.TextIOWrapper name='<stderr>' mode='w' encoding='utf-8'>, 'wsgi.multithread': True, 'wsgi.multiprocess': False, 'wsgi.run_once': False, 'wsgi.input': <_io.BytesIO object at 0x7fb398cbf680>, 'wsgi.file_wrapper': <class 'waitress.buffers.ReadOnlyFileBasedBuffer'>, 'wsgi.input_terminated': True, 'HTTP_HOST': 'csp.example.com', 'HTTP_USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36', 'CONTENT_LENGTH': '546', 'HTTP_ACCEPT': '*/*', 'HTTP_ACCEPT_ENCODING': 'gzip, deflate, br', 'HTTP_ACCEPT_LANGUAGE': 'en-DE,en-GB;q=0.9,en;q=0.8,de-DE;q=0.7,de;q=0.6,ro-RO;q=0.5,ro;q=0.4,en-US;q=0.3', 'CONTENT_TYPE': 'application/csp-report', 'HTTP_DNT': '1', 'HTTP_ORIGIN': 'https://xxxREDACTEDxxx', 'HTTP_REFERER': 'https://xxxREDACTEDxxx/', 'HTTP_SEC_FETCH_DEST': 'report', 'HTTP_SEC_FETCH_MODE': 'no-cors', 'HTTP_SEC_FETCH_SITE': 'cross-site', 'HTTP_X_FORWARDED_FOR': '2001:0DB8::1', 'HTTP_X_FORWARDED_HOST': 'csp.example.com', 'HTTP_X_FORWARDED_PORT': '443', 'HTTP_X_FORWARDED_PROTO': 'https', 'HTTP_X_FORWARDED_SERVER': '2319d1b2d5bf', 'HTTP_X_REAL_IP': '2001:0DB8::1', 'werkzeug.request': <Request 'http://csp.example.com/csp' [POST]>}
2020-12-06 14:38:27.135 INFO [csp.log_csp] {"csp-report": {"document-uri": "https://xxxREDACTEDxxx/", "referrer": "", "violated-directive": "style-src-attr", "effective-directive": "style-src-attr", "original-policy": "upgrade-insecure-requests; default-src 'self' https://cdnjs.cloudflare.com; script-src 'self' https://cdnjs.cloudflare.com https://s.ytimg.com; font-src https://fonts.gstatic.com https://cdnjs.cloudflare.com; report-uri https://csp.example.com/csp;", "disposition": "report", "blocked-uri": "inline", "line-number": 3, "column-number": 3968, "source-file": "https://cdnjs.cloudflare.com/ajax/libs/jquery/2.2.4/jquery.min.js", "status-code": 0, "script-sample": ""}}
2020-12-06 14:38:27.135 INFO [csp.log_csp] {"csp-report": {"document-uri": "https://xxxREDACTEDxxx/", "referrer": "", "violated-directive": "style-src-attr", "effective-directive": "style-src-attr", "original-policy": "upgrade-insecure-requests; default-src 'self' https://cdnjs.cloudflare.com; script-src 'self' https://cdnjs.cloudflare.com https://s.ytimg.com; font-src https://fonts.gstatic.com https://cdnjs.cloudflare.com; report-uri https://csp.example.com/csp;", "disposition": "report", "blocked-uri": "inline", "line-number": 911, "source-file": "https://xxxREDACTEDxxx/", "status-code": 0, "script-sample": ""}}
2020-12-06 14:38:27.136 DEBUG [csp.log_csp] {'REMOTE_ADDR': '10.0.14.14', 'REMOTE_HOST': '10.0.14.14', 'REMOTE_PORT': '56226', 'REQUEST_METHOD': 'POST', 'SERVER_PORT': '9180', 'SERVER_NAME': '9f02bb970b0b', 'SERVER_SOFTWARE': None, 'SERVER_PROTOCOL': 'HTTP/1.1', 'SCRIPT_NAME': '', 'PATH_INFO': '/csp', 'QUERY_STRING': '', 'wsgi.url_scheme': 'http', 'wsgi.version': (1, 0), 'wsgi.errors': <_io.TextIOWrapper name='<stderr>' mode='w' encoding='utf-8'>, 'wsgi.multithread': True, 'wsgi.multiprocess': False, 'wsgi.run_once': False, 'wsgi.input': <_io.BytesIO object at 0x7fb398c89860>, 'wsgi.file_wrapper': <class 'waitress.buffers.ReadOnlyFileBasedBuffer'>, 'wsgi.input_terminated': True, 'HTTP_HOST': 'csp.example.com', 'HTTP_USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_0_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36', 'CONTENT_LENGTH': '610', 'HTTP_ACCEPT': '*/*', 'HTTP_ACCEPT_ENCODING': 'gzip, deflate, br', 'HTTP_ACCEPT_LANGUAGE': 'en-DE,en-GB;q=0.9,en;q=0.8,de-DE;q=0.7,de;q=0.6,ro-RO;q=0.5,ro;q=0.4,en-US;q=0.3', 'CONTENT_TYPE': 'application/csp-report', 'HTTP_DNT': '1', 'HTTP_ORIGIN': 'https://xxxREDACTEDxxx', 'HTTP_REFERER': 'https://xxxREDACTEDxxx/', 'HTTP_SEC_FETCH_DEST': 'report', 'HTTP_SEC_FETCH_MODE': 'no-cors', 'HTTP_SEC_FETCH_SITE': 'cross-site', 'HTTP_X_FORWARDED_FOR': '2001:0DB8::1', 'HTTP_X_FORWARDED_HOST': 'csp.example.com', 'HTTP_X_FORWARDED_PORT': '443', 'HTTP_X_FORWARDED_PROTO': 'https', 'HTTP_X_FORWARDED_SERVER': '2319d1b2d5bf', 'HTTP_X_REAL_IP': '2001:0DB8::1', 'werkzeug.request': <Request 'http://csp.example.com/csp' [POST]>}
2020-12-06 14:38:27.137 INFO [csp.log_csp] {"csp-report": {"document-uri": "https://xxxREDACTEDxxx/", "referrer": "", "violated-directive": "style-src-elem", "effective-directive": "style-src-elem", "original-policy": "upgrade-insecure-requests; default-src 'self' https://cdnjs.cloudflare.com; script-src 'self' https://cdnjs.cloudflare.com https://s.ytimg.com; font-src https://fonts.gstatic.com https://cdnjs.cloudflare.com; report-uri https://csp.example.com/csp;", "disposition": "report", "blocked-uri": "inline", "line-number": 3, "column-number": 14649, "source-file": "https://cdnjs.cloudflare.com/ajax/libs/jquery/2.2.4/jquery.min.js", "status-code": 0, "script-sample": ""}}
```

Various errors (with `LOGLEVEL:DEBUG`):
```
2020-12-06 14:28:15.448 WARNING [csp.log_csp] Content too large (523445). Dropping.
2020-12-06 14:52:47.747 WARNING [csp.log_csp] Empty content received
2020-12-06 14:54:07.615 DEBUG [csp.log_csp] {'REMOTE_ADDR': '10.0.14.16', 'REMOTE_HOST': '10.0.14.16', 'REMOTE_PORT': '32772', 'REQUEST_METHOD': 'POST', 'SERVER_PORT': '9180', 'SERVER_NAME': '45d8708af6ab', 'SERVER_SOFTWARE': None, 'SERVER_PROTOCOL': 'HTTP/1.1', 'SCRIPT_NAME': '', 'PATH_INFO': '/csp', 'QUERY_STRING': '', 'wsgi.url_scheme': 'http', 'wsgi.version': (1, 0), 'wsgi.errors': <_io.TextIOWrapper name='<stderr>' mode='w' encoding='utf-8'>, 'wsgi.multithread': True, 'wsgi.multiprocess': False, 'wsgi.run_once': False, 'wsgi.input': <_io.BytesIO object at 0x7f8cbd65c0e0>, 'wsgi.file_wrapper': <class 'waitress.buffers.ReadOnlyFileBasedBuffer'>, 'wsgi.input_terminated': True, 'HTTP_HOST': 'csp.example.com', 'HTTP_USER_AGENT': 'curl/7.64.1', 'CONTENT_LENGTH': '10', 'HTTP_ACCEPT': '*/*', 'CONTENT_TYPE': 'application/x-www-form-urlencoded', 'HTTP_X_FORWARDED_FOR': '2001:0DB8::1', 'HTTP_X_FORWARDED_HOST': 'csp.example.com', 'HTTP_X_FORWARDED_PORT': '443', 'HTTP_X_FORWARDED_PROTO': 'https', 'HTTP_X_FORWARDED_SERVER': 'de9e6f88b502', 'HTTP_X_REAL_IP': '2001:0DB8::1', 'HTTP_ACCEPT_ENCODING': 'gzip', 'werkzeug.request': <Request 'http://csp.example.com/csp' [POST]>}
2020-12-06 14:54:07.616 DEBUG [csp.log_csp] Content is not JSON: `{"ab": e2}`
```

## Metrics

When setting `ENABLE_METRICS=yes`, the following metrics are exposed:
```
# HELP csp_valid_violation_reports_total Counts the number of valid violation reports
# TYPE csp_valid_violation_reports_total counter
csp_valid_violation_reports_total{blocked_uri="inline",document_uri="https://xxxREDACTEDxxx/",line_number="925",original_policy="upgrade-insecure-requests; default-src self https://cdnjs.cloudflare.com; script-src self https://cdnjs.cloudflare.com https://s.ytimg.com; font-src https://fonts.gstatic.com https://cdnjs.cloudflare.com; report-uri https://csp.example.com/csp;",violated_directive="script-src-elem"} 3.0
# HELP csp_valid_violation_reports_created Counts the number of valid violation reports
# TYPE csp_valid_violation_reports_created gauge
csp_valid_violation_reports_created{blocked_uri="inline",document_uri="https://xxxREDACTEDxxx/",line_number="925",original_policy="upgrade-insecure-requests; default-src self https://cdnjs.cloudflare.com; script-src self https://cdnjs.cloudflare.com https://s.ytimg.com; font-src https://fonts.gstatic.com https://cdnjs.cloudflare.com; report-uri https://csp.example.com/csp;",violated_directive="script-src-elem"} 1.607272996845561e+09
# HELP csp_invalid_violation_reports_total Counts the number of invalid violation reports
# TYPE csp_invalid_violation_reports_total counter
csp_invalid_violation_reports_total{reason="non-csp"} 2.0
csp_invalid_violation_reports_total{reason="non-json"} 1.0
csp_invalid_violation_reports_total{reason="empty"} 1.0
csp_invalid_violation_reports_total{reason="too-large"} 2.0
# HELP csp_invalid_violation_reports_created Counts the number of invalid violation reports
# TYPE csp_invalid_violation_reports_created gauge
csp_invalid_violation_reports_created{reason="non-csp"} 1.60727299902503e+09
csp_invalid_violation_reports_created{reason="non-json"} 1.607273003925279e+09
csp_invalid_violation_reports_created{reason="empty"} 1.607273008638792e+09
csp_invalid_violation_reports_created{reason="too-large"} 1.607273014508008e+09
# HELP csp_version_info Information about CSP
# TYPE csp_version_info gauge
csp_version_info{version="0.2.0-225909200"} 1.0
```

## Environment

| **Variable**             | **Default** | **Description**                                                        |
|:-------------------------|:-----------:|:-----------------------------------------------------------------------|
| `MAX_CONTENT_LENGTH`     | `32768`     | The maximum content length (in bytes) of the HTTP POST content         |
| `ENABLE_HEALTHZ_VERSION` | `no`        | Set this to `yes` to show the version on the `HEALTHZ_PATH` endpoint   |
| `ENABLE_METRICS`         | `no`        | Set this to `yes` to enable the Prometheus metrics                     |
| `CSP_PATH`               | `/csp`      | The path used for the CSP reporting                                    |
| `HEALTHZ_PATH`           | `/healthz`  | The path used for the healthcheck                                      |
| `METRICS_PATH`           | `/metrics`  | The path used for the the Prometheus metrics                           |
| `LOGLEVEL`               | `INFO`      | [Logging Level](https://docs.python.org/3/library/logging.html#levels) |
| `GELF_HOST`              | -           | If set, GELF UDP logging to this host will be enabled                  |
| `GELF_PORT`              | `12201`     | Ignored, if `GELF_HOST` is unset. The UDP port for GELF logging        |
| `PORT`                   | `9180`      | The port to bind to                                                    |
| `ADDRESS`                | `*`         | The IP address to bind to                                              |

## Breaking Changes
Starting with version `v0.1.0`, the log format has changed!

CSP will now parse and format any JSON received (smaller than `MAX_CONTENT_LENGTH`) and log it in form:
```
2020-12-06 14:59:13.855 INFO [csp.log_csp] {"ab": 2}
```

Non-JSON content will be logged as follows:
```
2020-12-06 15:15:58.497 DEBUG [csp.log_csp] Content is not JSON: `{"ab": e2}`
```

## Tags and Arch

Starting with version `v0.1.0`, the images are multi-arch, with builds for i386, amd64, arm64, armv7 and armv6.
* `vN.N.N` - for example v0.1.0
* `latest` - always pointing to the latest version
* `dev-branch` - the last build on a feature/development branch
* `dev-master` - the last build on the master branch

## Resources:
* GitLab: https://gitlab.com/ix.ai/csp
* GitHub: https://github.com/ix-ai/csp
* GitLab Registry: https://gitlab.com/ix.ai/csp/container_registry
* Docker Hub: https://hub.docker.com/r/ixdotai/csp
