# استخدام صورة بايثون من Docker Hub
FROM python:3.9-slim

# تحديد دليل العمل في الحاوية
WORKDIR /app

# نسخ المتطلبات إلى الحاوية
COPY requirements.txt .

# تثبيت المكتبات من requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# نسخ جميع الملفات الأخرى (main.py مثلا)
COPY . .

# تشغيل سكربت البوت
CMD ["python", "main.py"]
