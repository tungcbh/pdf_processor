# Giai đoạn 1: Build Stage
FROM python:3.9 AS builder
WORKDIR /app
COPY requirements.txt .
# Cài đặt phụ thuộc
RUN pip install --user -r requirements.txt

# Sao chép toàn bộ dự án
COPY . .

# Giai đoạn 2: Runtime Stage
FROM python:3.9-slim
WORKDIR /app
# Sao chép các thư viện đã cài từ builder
COPY --from=builder /root/.local /root/.local
# Sao chép mã nguồn
COPY --from=builder /app /app
# Đảm bảo pip và các thư viện trong PATH
ENV PATH=/root/.local/bin:$PATH
# Cổng ứng dụng lắng nghe
EXPOSE 8000
# Chạy ứng dụng
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]