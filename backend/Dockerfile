# ใช้ Python Image เล็กๆ
FROM python:3.9-slim

WORKDIR /app

# Copy dependency และ install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code ทั้งหมด
COPY . .

# เปิด Port 8080 (Cloud Run ชอบ Port นี้)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
