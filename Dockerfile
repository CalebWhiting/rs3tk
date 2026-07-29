# Test the rs3tk quick-start instructions in a clean environment.
#
# Build:   docker build -t rs3tk-test .
# Run:     docker run --rm -it rs3tk-test
# Shell:   docker run --rm -it --entrypoint bash rs3tk-test
#
# What this verifies:
#   1. uv sync          — Python deps install cleanly
#   2. pnpm install     — Node deps install cleanly
#   3. pnpm lint        — ruff passes
#   4. pnpm typecheck   — mypy passes
#   5. pnpm test        — pytest passes

FROM ubuntu:24.04 AS base

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# ── system packages ────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        ca-certificates \
        git \
        python3 python3-venv python3-dev \
    && rm -rf /var/lib/apt/lists/*

# ── uv (Python package manager) ───────────────────────────────────
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# ── Node.js 20.x + pnpm ──────────────────────────────────────────
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && npm install -g pnpm \
    && rm -rf /var/lib/apt/lists/*

# ── copy the repo ─────────────────────────────────────────────────
WORKDIR /app
COPY . .

# ── run the quick-start setup ─────────────────────────────────────
#    (mirrors the README instructions exactly)
RUN uv sync && pnpm install

# Make venv tools (ruff, mypy, pytest, rs3tk) available on PATH
ENV PATH="/app/.venv/bin:${PATH}"

# ── verify: lint, typecheck, tests ────────────────────────────────
CMD ["sh", "-c", "\
    echo '=== Lint ==='       && pnpm lint && \
    echo '=== Typecheck ==='  && pnpm typecheck && \
    echo '=== Tests ==='      && pnpm test && \
    echo '=== ALL PASSED ==='"]
