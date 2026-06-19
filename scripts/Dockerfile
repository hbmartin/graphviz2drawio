ARG UV_VERSION=0.11.19
FROM ghcr.io/astral-sh/uv:${UV_VERSION} AS uv

FROM ubuntu:24.04

ARG GRAPHVIZ_VERSION=15.0.0

ENV UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_PYTHON_INSTALL_DIR=/opt/uv-python \
    UV_PYTHON=3.12 \
    UV_LINK_MODE=copy \
    PATH="/opt/venv/bin:${PATH}"

WORKDIR /work

COPY --from=uv /uv /uvx /usr/local/bin/

RUN set -eux; \
    export DEBIAN_FRONTEND=noninteractive; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        curl \
        xz-utils; \
    mkdir -p /tmp/graphviz-debs; \
    curl -fsSL "https://gitlab.com/api/v4/projects/4207231/packages/generic/graphviz-releases/${GRAPHVIZ_VERSION}/ubuntu_24.04_graphviz-${GRAPHVIZ_VERSION}-debs.tar.xz" \
        | tar -xJ -C /tmp/graphviz-debs; \
    set -- $(find /tmp/graphviz-debs -type f \( \
        -name "graphviz_*.deb" \
        -o -name "libgraphviz4_*.deb" \
        -o -name "libgraphviz-dev_*.deb" \
    \) | sort); \
    test "$#" -eq 3; \
    apt-get install -y --no-install-recommends "$@"; \
    dot -V; \
    rm -rf /tmp/graphviz-debs /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./

RUN uv python install 3.12 \
    && uv sync --locked --no-install-project \
    && useradd --create-home --uid 10001 --shell /usr/sbin/nologin spec-runner \
    && chown spec-runner:spec-runner /work

ENV HOME=/tmp

USER spec-runner
