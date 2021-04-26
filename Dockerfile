# The Dockerfile tells Docker how to construct the image.
FROM mellesies/thomas-core:latest

LABEL maintainer="Melle Sieswerda <m.sieswerda@iknl.nl>"

# -- Defined in thomas-core:latest --
# ARG NB_USER=jupyter
# ARG NB_UID=1000
# ENV USER ${NB_USER}
# ENV NB_UID ${NB_UID}
# ENV HOME /home/${NB_USER}
# ENV THOMAS_DIR /home/${NB_USER}/thomas

# Copy package
USER root
# COPY . ${THOMAS_DIR}/thomas-server/
COPY thomas ${THOMAS_DIR}/thomas-server/thomas
COPY LICENSE ${THOMAS_DIR}/thomas-server/
COPY README.md ${THOMAS_DIR}/thomas-server/
COPY setup.py ${THOMAS_DIR}/thomas-server/

COPY config.yaml ${HOME}/config.yaml

RUN mkdir -p ${HOME}/.local/bin
RUN chown -R ${USER}:${USER} ${HOME}

WORKDIR ${THOMAS_DIR}
USER ${USER}
ENV PATH="${PATH}:${HOME}/.local/bin"


# thomas-core is already installed in the base image.
RUN pip install -e ./thomas-server

# Load fixtures here (users & networks) & run thomas!
WORKDIR ${HOME}

RUN thomas load-fixtures --environment=dev
RUN thomas load-fixtures --environment=prod

# thomas-server runs on port 5000
EXPOSE 5000

CMD thomas start --environment=prod
