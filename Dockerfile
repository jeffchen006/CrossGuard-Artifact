# syntax=docker/dockerfile:1

# ------------------------------------------------------------------------------
# Stage 1: Builder
# Compiles Foundry from a pinned commit using a robust build environment.
# ------------------------------------------------------------------------------
FROM ubuntu:22.04 AS foundry-builder

ARG DEBIAN_FRONTEND=noninteractive
ARG FOUNDRY_COMMIT=fdf5732d08ce1c67aa0aaf047c3fb86614caf5ae
ARG RUST_TOOLCHAIN=1.89.0

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    curl \
    git \
    pkg-config \
    libssl-dev \
    clang \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Install Rust (required for building Foundry)
ENV RUSTUP_HOME=/opt/rustup \
    CARGO_HOME=/opt/cargo
ENV PATH="/opt/cargo/bin:${PATH}"

RUN curl -sSf https://sh.rustup.rs | sh -s -- -y --profile minimal --default-toolchain "${RUST_TOOLCHAIN}"

# Build and install Foundry
RUN curl -L https://foundry.paradigm.xyz | bash \
    && /root/.foundry/bin/foundryup --commit "${FOUNDRY_COMMIT}"


# ------------------------------------------------------------------------------
# Stage 2: Runtime
# Merges the Python analysis environment with the compiled Foundry tools.
# ------------------------------------------------------------------------------
FROM python:3.10-slim

# Configuration
ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    MPLBACKEND=Agg \
    FOUNDRY_DISABLE_NIGHTLY_WARNING=1 \
    PATH="/root/.solc-select:/root/.vyper-select:/usr/local/bin:${PATH}"

# System Dependencies
# Combines requirements for Python numeric libraries and general utilities.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    ca-certificates \
    libssl-dev \
    libffi-dev \
    pkg-config \
    libfreetype6 \
    libpng16-16 \
    && rm -rf /var/lib/apt/lists/*

# Ensure python3 availability at standard paths
RUN if [ ! -e /usr/bin/python3 ]; then ln -s /usr/local/bin/python3 /usr/bin/python3; fi

# Copy Foundry binaries from builder
COPY --from=foundry-builder /root/.foundry/bin/forge /usr/local/bin/forge
COPY --from=foundry-builder /root/.foundry/bin/cast /usr/local/bin/cast
COPY --from=foundry-builder /root/.foundry/bin/anvil /usr/local/bin/anvil
COPY --from=foundry-builder /root/.foundry/bin/chisel /usr/local/bin/chisel

WORKDIR /app
COPY . /app

# Python Dependencies
ARG VYPER_SELECT_COMMIT=8cc58b2b2e25e7487515c2f0cb2743c25c042701
RUN pip install --upgrade pip \
    && pip install --no-cache-dir \
        tqdm \
        plotly \
        ujson \
        toml \
        requests \
        web3 \
        hexbytes \
        eth-abi \
        slither-analyzer \
        packaging \
        matplotlib \
        solc-select \
        "vyper-select @ git+https://github.com/jeffchen006/vyper-select.git@${VYPER_SELECT_COMMIT}"

# Solidity Management
# Installs versions for both the full experiments (0.8.17) and CrossGuard (0.8.26).
ARG SOLC_VERSIONS="0.8.17 0.8.26"
ARG SOLC_DEFAULT="0.8.17"
RUN solc-select install ${SOLC_VERSIONS} \
    && solc-select use ${SOLC_DEFAULT}

# Vyper Management
ARG VYPER_VERSIONS="0.3.7 0.2.16"
ARG VYPER_DEFAULT="0.3.7"
RUN vyper-select install ${VYPER_VERSIONS} \
    && vyper-select use ${VYPER_DEFAULT}

# Entrypoint
# Default to the full experiment suite. 
# For gas experiments: docker run ... python3 gas_experiment.py --solc solc
CMD ["python3", "runFullExperiments.py"]
