FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
RUN addgroup --system django && adduser --system --ingroup django django
COPY requirements.txt ./
RUN python -m pip install --upgrade pip && python -m pip install -r requirements.txt
COPY --chown=django:django . .
RUN cp /app/docker/entrypoint.sh /usr/local/bin/global-exchange-entrypoint \
    && chmod +x /usr/local/bin/global-exchange-entrypoint
USER django
EXPOSE 8000
ENTRYPOINT ["/usr/local/bin/global-exchange-entrypoint"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
