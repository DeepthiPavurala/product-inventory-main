FROM python:3.11-slim

# Create non-root user
RUN addgroup --system appgroup && adduser --system --group appuser

WORKDIR /app

COPY Pipfile requirements.txt ./
RUN pip install --no-cache-dir pipenv \
    && pipenv install --system --skip-lock \
    || pip install --no-cache-dir -r requirements.txt

COPY . .

# Make entrypoint executable
RUN chmod +x entrypoint.sh

# Change ownership
RUN chown -R appuser:appgroup /app

USER appuser

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]