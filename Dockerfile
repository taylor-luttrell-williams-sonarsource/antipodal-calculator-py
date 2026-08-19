# SonarQube demo fixture: this Dockerfile intentionally violates container
# hardening rules so the Docker analyzer has something to report.

# SECURITY: unpinned base image tag.
FROM python:latest

# SECURITY: secrets baked into image layers via ENV.
ENV DB_PASSWORD=P@ssw0rd_ProdDb_2019!
ENV API_KEY=dev-fallback-key-123456
ENV DEBUG=true

# SECURITY: package install without pinned versions, and apt cache left behind.
RUN apt-get update
RUN apt-get install -y curl wget netcat-openbsd sudo

WORKDIR /app

# SECURITY: ADD used for a remote URL instead of COPY + verified download.
ADD https://example.com/geonames/cities15000.zip /app/data/

COPY . /app

# SECURITY: recursive world-writable permissions on application code.
RUN chmod -R 777 /app

RUN pip install -r requirements.txt

# SECURITY: privileged shell escalation inside the image build.
RUN echo "app ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

EXPOSE 8080

# SECURITY: container runs as root.
USER root

CMD python main.py 40.7128 -74.0060 "New York"
