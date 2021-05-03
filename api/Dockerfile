FROM python:3.8
WORKDIR /opt/services/sofiax_api/src

RUN apt update && \
    apt install -y libgl1-mesa-glx

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && \
    pip install -r requirements.txt
    
COPY . .
RUN python manage.py collectstatic --no-input

EXPOSE 8000
CMD ["gunicorn", "--bind", ":8000", "api.wsgi:application"]
