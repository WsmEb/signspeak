# ── Stage: runtime ────────────────────────────────────────────────────────────
# python:3.11-alpine is ~50 MB vs ~900 MB for the full image
FROM python:3.11-alpine

# Build deps needed only to compile some Python C-extensions (numpy, etc.)
# We install then remove them in the same layer to keep the image small
RUN apk add --no-cache --virtual .build-deps \
        gcc \
        musl-dev \
        linux-headers \
    && pip install --no-cache-dir \
        fastapi==0.110.0 \
        uvicorn==0.27.1 \
        numpy==1.26.4 \
        pydantic==2.6.3 \
        python-multipart==0.0.9 \
    && apk del .build-deps

# Non-root user for security
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
WORKDIR /app
COPY main.py .
RUN chown -R appuser:appgroup /app
USER appuser

EXPOSE 8000

# --host 0.0.0.0 so Docker can route traffic into the container
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
