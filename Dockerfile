FROM python:3.11-slim
COPY --from=ghcr.io/astral-sh/uv:0.8.4 /uv /usr/local/bin/uv
WORKDIR /srv
ENV UV_LINK_MODE=copy PATH="/srv/.venv/bin:$PATH" ARTIFACT_DIR=/srv/artifacts
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY src ./src
RUN uv sync --frozen --no-dev
# Download the UCI Online Retail data and fit the model at build time (data is not committed).
ARG N_CLUSTERS=4
RUN N_CLUSTERS=$N_CLUSTERS python -m segmentation.build
EXPOSE 8000
HEALTHCHECK --interval=10s --timeout=3s --retries=10 CMD python -c "import urllib.request;urllib.request.urlopen('http://localhost:8000/health')"
CMD ["uvicorn", "segmentation.api:app", "--host", "0.0.0.0", "--port", "8000"]
