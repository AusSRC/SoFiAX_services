FROM python:3.8
WORKDIR /opt/services/sofia_web_app/src

RUN apt update && \
    apt install -y libgl1-mesa-glx

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && \
    pip install -r requirements.txt
    
COPY . /opt/services/sofia_web_app/src

RUN python sofiax_web/manage.py collectstatic --no-input

EXPOSE 8000

CMD ["gunicorn", "--chdir", "sofiax_web", "--bind", ":8000", "sofiax_web.wsgi:application"]
