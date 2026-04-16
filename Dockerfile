# Gunakan image Python yang ringan
FROM python:3.10-slim

# Set folder kerja di dalam container
WORKDIR /app

# Install library OS yang dibutuhkan untuk psycopg2 (PostgreSQL)
RUN apt-get update && apt-get install -y libpq-dev gcc

# Copy file requirements dan install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy seluruh kode aplikasi
COPY . .

# Buka port 5000 (sesuai Flask)
EXPOSE 5000

# Jalankan aplikasinya
CMD ["python", "app.py"]