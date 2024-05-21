FROM alpine:latest as builder

COPY csp/requirements.txt /work/csp/requirements.txt

ENV CRYPTOGRAPHY_DONT_BUILD_RUST="1"

RUN set -xeu; \
    mkdir -p /work/wheels; \
    apk add \
      py3-pip \
      gcc \
      python3-dev \
      musl-dev \
      linux-headers \
    ; \
    pip3 install -U --break-system-packages \
      wheel \
      pip

RUN pip3 wheel --prefer-binary -r /work/csp/requirements.txt -w /work/wheels

FROM alpine:latest
LABEL maintainer="docker@ix.ai" \
      ai.ix.repository="ix.ai/csp" \
      org.opencontianers.image.description="A basic Content Security Policy processor running in docker"

COPY --from=builder /work /

RUN set -xeu; \
    apk add --no-cache \
        python3 \
        py3-pip \
    ; \
    pip3 install \
        --no-index \
        --no-cache-dir \
        --find-links /wheels \
        --break-system-packages \
        -r /csp/requirements.txt \
    ; \
    rm -rf /wheels

COPY csp/ /csp
COPY csp.sh /usr/local/bin/csp.sh

EXPOSE 9180

ENTRYPOINT ["/usr/local/bin/csp.sh"]
