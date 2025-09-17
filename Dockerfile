# Read the doc: https://huggingface.co/docs/hub/spaces-sdks-docker
# HF Spaces Docker setup for Excel Interview AI

FROM python:3.11-slim

# Create non-root user as required by HF Spaces
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

# Copy requirements and install Python dependencies
COPY --chown=user requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the entire application
COPY --chown=user . /app

# Set environment variables
ENV PYTHONPATH=/app/server
ENV PORT=7860

# Expose the port
EXPOSE 7860

# Command to run the application
CMD ["python", "app.py"]
