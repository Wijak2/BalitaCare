FROM python:3.10-slim

# 1. Install system dependencies needed by pandas, openpyxl, and others
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 2. Set workdir
WORKDIR /app

# 3. Copy requirements (better caching)
COPY requirements.txt .

# 4. Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy your backend source code
COPY . .

# 6. Expose port for Gunicorn
EXPOSE 5000

# 7. Run app with Gunicorn for production
# Ubah app:app sesuai nama file dan objek Flask kamu!
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
