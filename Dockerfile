FROM docker:latest

LABEL maintainer='ix.ai <docker@ix.ai>'

WORKDIR /app

COPY src/ /app

RUN apk add --no-cache python3 && \
    pip3 install --no-cache-dir -r requirements.txt

EXPOSE 9180

ENTRYPOINT ["python3", "/app/csp.py"]
