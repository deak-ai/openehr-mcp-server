FROM python:alpine

WORKDIR /app

# No additional system dependencies needed

# Copy version file first for layer caching
COPY VERSION .

# Install pip and requirements directly (more Docker-friendly approach)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Set environment variables
ENV PYTHONPATH=/app

# Add version label
LABEL org.opencontainers.image.version="$(cat VERSION)"
LABEL org.opencontainers.image.authors="CTO DEAK AI"
LABEL org.opencontainers.image.title="OpenEHR MCP Server"
LABEL org.opencontainers.image.description="Model Context Protocol (MCP) server for OpenEHR integration"

# Command to run the MCP server
CMD ["python", "src/openehr_mcp_server.py"]
