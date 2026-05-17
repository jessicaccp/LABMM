# ── base: install dependencies ─────────────────────────────────────────────────
FROM python:3.13-slim AS base

WORKDIR /app

ENV FLASK_APP=run.py

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── dev: Flask development server with hot-reload ──────────────────────────────
FROM base AS dev

COPY . .
RUN chmod +x entrypoint.sh

EXPOSE 5000

ENTRYPOINT ["./entrypoint.sh"]
CMD ["flask", "run", "--host=0.0.0.0", "--reload"]

# ── prod: Gunicorn production server ──────────────────────────────────────────
FROM base AS prod

COPY . .
RUN chmod +x entrypoint.sh

EXPOSE 5000

ENTRYPOINT ["./entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "run:app"]
