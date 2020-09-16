FROM tiangolo/meinheld-gunicorn-flask:python3.8

COPY ./requirements.txt /tmp/
RUN pip install -r /tmp/requirements.txt

COPY ./build/prestart.sh /app/
RUN chmod +x /app/prestart.sh

COPY ./ /app
