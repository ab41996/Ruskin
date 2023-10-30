FROM python:3-alpine3.11
WORKDIR /app
RUN pip install poetry
COPY . /app
RUN poetry install
EXPOSE 3000
CMD python ./app.py
