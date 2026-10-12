FROM python:3.12
WORKDIR /opt/services/survey_web/src

RUN apt update && \
    apt install -y libgl1-mesa-dev libglib2.0-0

# Dependencies are installed from pyproject.toml and uv.lock of the repository (the build context)
COPY pyproject.toml uv.lock /opt/services/project/
RUN pip install --upgrade pip uv && \
    cd /opt/services/project && \
    UV_PROJECT_ENVIRONMENT=/usr/local uv sync --locked --inexact --no-dev --no-install-project

COPY app/ .

EXPOSE 8000
# Static files are collected on startup because the settings need the environment variables of the deployment
CMD ["sh", "-c", "python manage.py collectstatic --no-input && exec gunicorn --bind :8000 --keep-alive 5000 --timeout 5000 --workers 8 config.wsgi:application --access-logfile - --error-logfile - --log-level debug"]
