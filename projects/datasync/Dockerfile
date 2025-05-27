# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install uv
RUN pip install uv

# Set the working directory in the container
WORKDIR /app

# Copy root project configuration (if needed by libs or datasync indirectly)
# Source: <build_context>/pyproject.toml -> Destination: /app/pyproject.toml
COPY pyproject.toml uv.lock* ./

# Copy library-specific pyproject.toml files
# Source: <build_context>/libs/coreutils/pyproject.toml -> Destination: /app/libs/coreutils/pyproject.toml
COPY libs/coreutils/pyproject.toml ./libs/coreutils/
COPY libs/datastore/pyproject.toml ./libs/datastore/
COPY libs/kafkalib/pyproject.toml ./libs/kafkalib/

# Copy datasync project's pyproject.toml and uv.lock
# Source: <build_context>/projects/datasync/pyproject.toml -> Destination: /app/projects/datasync/pyproject.toml
COPY projects/datasync/pyproject.toml projects/datasync/uv.lock* ./projects/datasync/

# Copy all library code
# Source: <build_context>/libs -> Destination: /app/libs
COPY libs ./libs/

# Copy all datasync application code
# Source: <build_context>/projects/datasync -> Destination: /app/projects/datasync
COPY projects/datasync ./projects/datasync/

# Install Python dependencies for the datasync project
# This assumes projects/datasync/pyproject.toml is correctly set up.
# The path ./projects/datasync/pyproject.toml is relative to WORKDIR /app
RUN uv pip install --system -r ./projects/datasync/pyproject.toml

# Command to run the application
# The path ./projects/datasync/main.py is relative to WORKDIR /app
CMD ["python", "./projects/datasync/main.py"]