FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# Copy workspace root files for dependency resolution
COPY pyproject.toml uv.lock ./

# Copy package files and source
COPY apps/core ./apps/core/
COPY apps/chatbot_ui ./apps/chatbot_ui/

ENV UV_COMPILE_BYTECODE=1

# Install dependencies including workspace packages
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --package chatbot-ui

# Enable bytecode compilation and Python optimization
ENV PYTHONOPTIMIZE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set PATH to use the virtual environment
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/apps:/app/apps/chatbot_ui/src:$PYTHONPATH"

# Create non-root user and set permissions
RUN addgroup --system app && \
    adduser --system --ingroup app app && \
    chown -R app:app /app && \
    mkdir -p /home/app && \
    chown -R app:app /home/app && \
    mkdir -p /home/app/.streamlit && \
    mkdir -p /home/app/.streamlit/data && \
    mkdir -p /home/app/.streamlit/cache && \
    chown -R app:app /home/app/.streamlit

# Switch to non-root user
USER app

# Expose the Streamlit port
EXPOSE 8501

WORKDIR /app/apps/chatbot_ui/src

ENV HOME=/home/app
# Command to run the application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
