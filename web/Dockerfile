FROM python:3.10
WORKDIR /opt/services/survey_web/src

RUN apt update && \
    apt install -y libgl1-mesa-glx

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && \
    pip install -r requirements.txt
    
COPY . .
RUN python manage.py collectstatic --no-input

EXPOSE 8000
CMD ["gunicorn", "--bind", ":8000", "survey_web.wsgi:application"]
