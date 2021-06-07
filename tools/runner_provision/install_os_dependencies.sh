#!/bin/bash -e

# Install dependencies
dpkg --add-architecture i386 && \
    apt-get update && \
    apt-get install -y  --no-install-recommends -o APT::Immediate-Configure=false \
    libncurses5:i386 \
    libc6:i386 \
    libstdc++6:i386 \
    lib32gcc1 \
    lib32ncurses6 \
    lib32z1 \
    zlib1g:i386 \
    openjdk-8-jdk \
    git \
    wget \
    unzip \
    git-lfs \
    curl \
    qt5-default \
    zip unzip \
    sshpass \
    apt-transport-https \
    ca-certificates \
    gnupg-agent \
    gettext \
    liblttng-ust0 \
    libcurl4-openssl-dev \
    inetutils-ping \
    jq \
    tar \
    psmisc \
    net-tools \
    openssh-client \
    supervisor \
    ccache

# Install Python dependencies
apt-get install python3
apt-get install -y --no-install-recommends python3-pip
pip3 install -r /requirements.txt