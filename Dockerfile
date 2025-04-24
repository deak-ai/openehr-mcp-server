FROM python:alpine

WORKDIR /app

# No additional system dependencies needed

# Install pip and requirements directly (more Docker-friendly approach)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/

# Set environment variables
ENV PYTHONPATH=/app

# Command to run the MCP server
CMD ["python", "src/openehr_mcp_server.py"]
