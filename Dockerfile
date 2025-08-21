# Use uv + Python 3.12 base to avoid apt installs
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Set working dir
WORKDIR /app

# Install minimal OS packages needed for patching
RUN apt-get update && apt-get install -y --no-install-recommends git patch \
    && rm -rf /var/lib/apt/lists/*

# Copy project metadata and install deps with uv
COPY pyproject.toml uv.lock ./
RUN uv sync

# Ensure the app uses the created virtualenv
ENV VIRTUAL_ENV="/app/.venv"
ENV PATH="/app/.venv/bin:${PATH}"

# Ensure Python can import from project root
ENV PYTHONPATH="/app"

# Copy source
COPY . .

RUN git init && \
    git config user.name "user" && \
    git config user.email "user@example.com" && \
    git add . && \
    git commit -m "Initial commit" --allow-empty

# Keep container running
CMD ["tail", "-f", "/dev/null"]