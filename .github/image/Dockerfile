# Run image for one commit: toolchain, Python 3.7 with locked packages, and the built simulator.
# Build context = repository root. Built and pushed by .github/workflows/build-image.yml as
#   ghcr.io/<owner>/mac-world-run:<commit sha>
# Every pack pulls it by digest, so no package is installed at run time (finalized plan, Reproducibility).
FROM ubuntu:22.04@sha256:74b12b11ffa550fba1929ad4d8d16533c34f6612728469671afba1b03b66881c

ARG APT_SNAPSHOT=20261114T000000Z
ARG MICROMAMBA_VERSION=2.0.5-0
ARG MICROMAMBA_SHA256=cdf5a2e18d213617b6c5c32d8763b4e8fc05f8173b4f4017997683cb984357eb
ENV DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC

# apt from a dated snapshot, so the same Dockerfile gives the same compiler and libraries later.
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates \
 && sed -i "s|http://archive.ubuntu.com/ubuntu/\?|https://snapshot.ubuntu.com/ubuntu/${APT_SNAPSHOT}/|g; s|http://security.ubuntu.com/ubuntu/\?|https://snapshot.ubuntu.com/ubuntu/${APT_SNAPSHOT}/|g" /etc/apt/sources.list \
 && apt-get update \
 && apt-get install -y --no-install-recommends build-essential git curl bzip2 tar pkg-config \
      python3 python3-dev python-is-python3 libprotobuf-dev protobuf-compiler libzmq3-dev libxml2-dev libsqlite3-dev sqlite3 \
 && rm -rf /var/lib/apt/lists/*

RUN curl -sSL -o /usr/local/bin/micromamba "https://github.com/mamba-org/micromamba-releases/releases/download/${MICROMAMBA_VERSION}/micromamba-linux-64" \
 && echo "${MICROMAMBA_SHA256}  /usr/local/bin/micromamba" | sha256sum -c - \
 && chmod +x /usr/local/bin/micromamba \
 && micromamba create -y -p /opt/venv37-conda -c conda-forge "python=3.7.12=hf930737_100_cpython" \
 && /opt/venv37-conda/bin/python -m venv /opt/venv37 \
 && micromamba clean -a -y

COPY .github/image/requirements-lock.txt /tmp/requirements-lock.txt
RUN /opt/venv37/bin/python -m pip install --no-cache-dir --upgrade "pip<24.1" \
 && /opt/venv37/bin/pip install --no-cache-dir -r /tmp/requirements-lock.txt \
 && rm -f /tmp/requirements-lock.txt

# Source and build. .dockerignore keeps .git, docs figures and old results out of the context.
COPY ns-3.29 /opt/mac-world/ns-3.29
COPY .github/scripts /opt/mac-world/.github/scripts
WORKDIR /opt/mac-world/ns-3.29
# ns3gym is installed after configure: waf configure generates its messages_pb2.py.
RUN ./waf configure > /tmp/configure.log 2>&1 && ./waf build > /tmp/build.log 2>&1 \
 && /opt/venv37/bin/pip install --no-cache-dir --no-deps ./contrib/opengym/model/ns3gym \
 && ./waf --run "scratch/linear-mesh/linear-mesh --nWifi=5 --dryRun=true --disableGym=true --seed=1 --simTime=2" > /tmp/dry.log 2>&1 \
 && tail -3 /tmp/dry.log

ARG GIT_SHA=unknown
ENV MACWORLD_COMMIT=${GIT_SHA} MACWORLD_PY=/opt/venv37/bin/python
LABEL org.opencontainers.image.revision=${GIT_SHA}
WORKDIR /opt/mac-world/ns-3.29/scratch/linear-mesh
