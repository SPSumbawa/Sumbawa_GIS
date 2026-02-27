FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies (needed for pyogrio/gdal)
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set Environment Variables for GDAL
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
# Using --no-cache-dir to keep image small
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (FastAPI default)
EXPOSE 8000

# Volume for Data (Your NAS folder will be mounted here)
# /app/data_shps -> Where to put ZIPs
# /app/index_storage -> Where valid index.gpkg will be stored
VOLUME ["/app/data_shps", "/app/index_storage"]

# Override config to use volume paths via Env Vars or just code assumption
# Better to use ENV vars in code, but for now we map volumes to existing structure
ENV DATA_DIR=/app/data_shps
ENV INDEX_FILE=/app/index_storage/index.gpkg

# Command to run server
CMD ["python", "-m", "app.main"]
