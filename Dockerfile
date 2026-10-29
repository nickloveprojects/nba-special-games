FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV NBA_DATA_DIR=/app/data
EXPOSE 8000
# Runs the dashboard and the 8am scheduler together
CMD ["sh", "-c", "python -m app.cli daemon & python -m app.cli serve --port 8000"]
