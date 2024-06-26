FROM alpine:latest
LABEL maintainer="docker@ix.ai" \
      ai.ix.repository="ix.ai/csp" \
      org.opencontianers.image.description="A basic Content Security Policy processor running in docker"

COPY csp/requirements.txt /csp/requirements.txt

RUN apk add --no-cache python3 py3-pip py3-waitress py3-flask py3-prometheus-client && \
    pip3 install --break-system-packages --no-cache-dir -r /csp/requirements.txt

COPY csp/ /csp
COPY csp.sh /usr/local/bin/csp.sh

EXPOSE 9180

ENTRYPOINT ["/usr/local/bin/csp.sh"]
