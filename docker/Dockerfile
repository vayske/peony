FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive
ARG GIT_PAT
ARG RUMINA_GIT=https://${GIT_PAT}@github.com/vayske/Rumina.git
ARG BRANCH

ENV LANG=C.UTF-8
ENV RUMINA_HOME=/home/rumina
ENV RUMINA_DIR=${RUMINA_HOME}/Rumina
ENV MIRAI_DIR=${RUMINA_HOME}/Mirai

RUN apt-get update && apt-get install -y \
    git \
    screen \
    curl \
    openjdk-16-jre \
    python3.8-distutils \
    firefox \
    firefox-geckodriver \
&&  apt-get clean \
&&  rm -rf /var/lib/apt/lists/*

RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py

RUN python3 get-pip.py \
&&  rm get-pip.py

RUN mkdir -p ${RUMINA_HOME} \
&&  cd ${RUMINA_HOME} \
&&  git clone -b ${BRANCH} --progress ${RUMINA_GIT} .

RUN pip install -r ${RUMINA_DIR}/requirements.txt

RUN cd ${RUMINA_HOME} \
&&  rm -rf .git* 

ENTRYPOINT [ "/home/rumina/docker/init.sh" ]


