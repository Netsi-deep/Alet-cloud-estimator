# Use a clean, lightweight Python base image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Install dependencies directly
RUN pip install --no-cache-dir fastapi uvicorn pydantic reportlab

# Copy the rest of the application code and static files into the container
COPY . /app

# Expose port 8000 to allow outside access
EXPOSE 8000

# Run the FastAPI server using Uvicorn
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}