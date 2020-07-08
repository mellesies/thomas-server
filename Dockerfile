# The Dockerfile tells Docker how to construct the image.
FROM mellesies/thomas-core:latest

LABEL maintainer="Melle Sieswerda <m.sieswerda@iknl.nl>"

USER root


# Copy package
COPY . /usr/local/python/thomas-server/
COPY config.yaml /config.yaml

WORKDIR /usr/local/python/

# thomas-core is already installed in the base image.
RUN pip install -e ./thomas-server

# Load fixtures here (users & networks) & run thomas!
# WORKDIR /usr/local/python/thomas-server/
WORKDIR /

# Shortcuts for convenience
# RUN ln -s /usr/local/lib/python3.8/site-packages ./
# RUN ln -s /root/.local/share/thomas ./

RUN thomas load-fixtures --environment=dev
RUN thomas load-fixtures --environment=prod

# thomas-server runs on port 5000
EXPOSE 5000

CMD thomas start --environment=prod
