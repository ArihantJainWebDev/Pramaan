FROM python:3.12-slim

# Install system dependencies (C compiler, CMake for liboqs, etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    libssl-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Run API by default
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
