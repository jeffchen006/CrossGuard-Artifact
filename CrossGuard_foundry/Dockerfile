# syntax=docker/dockerfile:1
#
# Reproducible environment for CrossGuard gas experiments.
#
# Pins:
# - Foundry (forge/cast/anvil/chisel) to a specific commit
# - solc to an exact version (default: 0.8.26)
#
# Build:
#   docker build -t crossguard-gas \
#     --build-arg FOUNDRY_COMMIT=fdf5732d08ce1c67aa0aaf047c3fb86614caf5ae \
#     --build-arg SOLC_VERSION=0.8.26 \
#     .
#
# Run:
#   docker run --rm -t crossguard-gas
#

ARG UBUNTU_VERSION=22.04
ARG FOUNDRY_COMMIT=fdf5732d08ce1c67aa0aaf047c3fb86614caf5ae
ARG SOLC_VERSION=0.8.26

FROM ubuntu:${UBUNTU_VERSION} AS foundry-builder

ARG DEBIAN_FRONTEND=noninteractive
ARG FOUNDRY_COMMIT

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    git \
    build-essential \
    pkg-config \
    libssl-dev \
    clang \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Install Rust (needed because we build Foundry from a pinned commit).
ENV RUSTUP_HOME=/opt/rustup \
    CARGO_HOME=/opt/cargo
ENV PATH="/opt/cargo/bin:${PATH}"
RUN curl -sSf https://sh.rustup.rs | sh -s -- -y --profile minimal --default-toolchain stable

# Install foundryup, then build & install Foundry from the pinned commit.
RUN curl -L https://foundry.paradigm.xyz | bash
RUN /root/.foundry/bin/foundryup --commit "${FOUNDRY_COMMIT}"


FROM ubuntu:${UBUNTU_VERSION} AS runtime

ARG DEBIAN_FRONTEND=noninteractive
ARG SOLC_VERSION

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    git \
    python3 \
    && rm -rf /var/lib/apt/lists/*

# Install a pinned solc binary.
# Source: Solidity GitHub releases. (Pinned version via SOLC_VERSION build-arg.)
RUN curl -L "https://github.com/ethereum/solidity/releases/download/v${SOLC_VERSION}/solc-static-linux" \
      -o /usr/local/bin/solc \
    && chmod +x /usr/local/bin/solc \
    && /usr/local/bin/solc --version

# Copy Foundry binaries from builder stage.
COPY --from=foundry-builder /root/.foundry/bin/forge /usr/local/bin/forge
COPY --from=foundry-builder /root/.foundry/bin/cast /usr/local/bin/cast
COPY --from=foundry-builder /root/.foundry/bin/anvil /usr/local/bin/anvil
COPY --from=foundry-builder /root/.foundry/bin/chisel /usr/local/bin/chisel

ENV PATH="/usr/local/bin:${PATH}" \
    FOUNDRY_DISABLE_NIGHTLY_WARNING=1

WORKDIR /app
COPY . /app

# Default: run the experiment and compare to expected.txt.
CMD ["python3", "gas_experiment.py", "--solc", "/usr/local/bin/solc"]



