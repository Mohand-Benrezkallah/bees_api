FROM python:3.12-slim

WORKDIR /app

# Set Python path to include the current directory
ENV PYTHONPATH=/app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for uploaded images if it doesn't exist
RUN mkdir -p bees_api/app/images

# Run the application
CMD ["uvicorn", "bees_api.app.main:app", "--host", "0.0.0.0", "--port", "8000"]