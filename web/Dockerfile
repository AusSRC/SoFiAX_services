FROM python:3.12
WORKDIR /opt/services/survey_web/src

RUN apt update && \
    apt install -y libgl1-mesa-dev libglib2.0-0

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . .

EXPOSE 8000
# Static files are collected on startup because the settings need the environment variables of the deployment
CMD ["sh", "-c", "python manage.py collectstatic --no-input && exec gunicorn --bind :8000 --keep-alive 5000 --timeout 5000 --workers 8 config.wsgi:application --access-logfile - --error-logfile - --log-level debug"]
