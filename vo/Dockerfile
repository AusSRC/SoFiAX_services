ARG DEBIAN_IMAGE="latest"
FROM "debian:$DEBIAN_IMAGE"

RUN apt-get update && apt-get -y upgrade && \
    apt-get install -y subversion python3 python3-setuptools python3-pip \
    curl git gnupg2 locales sudo vim wget  

ARG APT_REPO="release" 

# This is the brute-force solution for Debian
ENV LC_ALL=C.UTF-8
RUN echo LC_ALL="$LC_ALL" > /etc/default/locale

RUN echo "deb http://vo.ari.uni-heidelberg.de/debian ${APT_REPO} main" \
        > /etc/apt/sources.list.d/gavo.list                         && \
    wget -qO - http://docs.g-vo.org/archive-key.asc | apt-key add -


RUN DEBIAN_FRONTEND='noninteractive'                  && \
    apt-get update                                    && \
    apt-get install -y python3-gavo       && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
    
ENV GAVO_ROOT="/var/gavo"
ENV GAVO_INPUTS="${GAVO_ROOT}/inputs"
ENV GAVO_SETTINGS="/etc/gavo.rc"

RUN adduser --system gavo && \
    addgroup --system gavo && \
    adduser gavo gavo && \
    adduser `id -nu` gavo &&\
    mkdir -p "${GAVO_ROOT}"


RUN gavo init --nodb
COPY gavo.rc /etc/gavo.rc
COPY defaultmeta.txt ${GAVO_ROOT}/etc/defaultmeta.txt
COPY dsn ${GAVO_ROOT}/etc/dsn
COPY feed ${GAVO_ROOT}/etc/feed
COPY trustedquery ${GAVO_ROOT}/etc/trustedquery
COPY untrustedquery ${GAVO_ROOT}/etc/untrustedquery
COPY startup.sh /startup.sh

RUN mkdir -p ${GAVO_INPUTS}/survey
COPY vo.rd ${GAVO_INPUTS}/survey/vo.rd

RUN chmod +x /startup.sh
CMD /startup.sh
