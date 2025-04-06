FROM public.ecr.aws/docker/library/alpine:3.21.3@sha256:a8560b36e8b8210634f77d9f7f9efd7ffa463e380b75e2e74aff4511df3ef88c AS builder

COPY csp/requirements.txt /work/csp/requirements.txt

ENV CRYPTOGRAPHY_DONT_BUILD_RUST="1"

RUN set -xeu; \
    mkdir -p /work/wheels; \
    apk add \
      py3-pip \
      python3-dev \
      openssl-dev \
      gcc \
      musl-dev \
      libffi-dev \
      make \
      openssl-dev \
      cargo \
    ; \
    pip3 install -U --break-system-packages \
      wheel \
      pip

RUN pip3 wheel --prefer-binary -r /work/csp/requirements.txt -w /work/wheels

FROM public.ecr.aws/docker/library/alpine:3.21.3@sha256:a8560b36e8b8210634f77d9f7f9efd7ffa463e380b75e2e74aff4511df3ef88c

LABEL maintainer="csp@docker.egos.tech" \
      ai.ix.repository="ix.ai/csp" \
      org.opencontianers.image.description="A basic Content Security Policy processor running in docker" \
      org.opencontainers.image.source="https://gitlab.com/ix.ai/csp"

COPY --from=builder /work /

RUN set -xeu; \
    ls -lashi /wheels; \
    apk upgrade --no-cache; \
    apk add --no-cache py3-pip; \
    pip3 install --no-cache-dir --break-system-packages -U pip;\
    pip3 install \
      --no-index \
      --no-cache-dir \
      --find-links /wheels \
      --break-system-packages \
      --requirement /csp/requirements.txt \
    ; \
    rm -rf /wheels

COPY csp/ /csp
COPY csp.sh /usr/local/bin/csp.sh

EXPOSE 9180

ENTRYPOINT ["/usr/local/bin/csp.sh"]
