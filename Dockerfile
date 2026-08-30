FROM python:3.10
WORKDIR /app

ADD requirements.txt /app/requirements.txt

RUN pip install --upgrade -r requirements.txt

EXPOSE 3001

COPY ./ /app

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "3001"]