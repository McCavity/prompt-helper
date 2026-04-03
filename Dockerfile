FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_ENV=production
ENV PORT=5000
# Override this in production: docker run -e SECRET_KEY=your-secret ...
ENV SECRET_KEY=change-me-in-production

EXPOSE ${PORT}

VOLUME ["/app/instance"]

CMD ["python", "app.py"]
