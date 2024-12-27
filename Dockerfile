FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

ENV PYTHONUNBUFFERED=1
# ENV UV_COMPILE_BYTECODE=1 # TODO: Uncomment when production-ready
ENV UV_NO_CACHE=1

WORKDIR /app

COPY . .
RUN uv sync --frozen --no-install-project

CMD ["fastapi", "run"]
