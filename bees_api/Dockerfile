FROM python:3.12-slim

WORKDIR /src

# Set Python path to include the current directory
ENV PYTHONPATH=/src

# Add a cache-busting argument that can be used to force rebuilds
ARG CACHEBUST=1

# Install dependencies first (this rarely changes)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (this changes more frequently)
COPY . .

# Create directory for uploaded images if it doesn't exist
RUN mkdir -p /src/app/images

# Run the application
CMD ["uvicorn", "bees_api.app.main:app", "--host", "0.0.0.0", "--port", "8000"]