FROM python:3.11
RUN pip install --upgrade pip
RUN pip install poetry

WORKDIR /app
COPY . /app

RUN poetry config virtualenvs.create false
RUN poetry install --no-dev

# ENTRYPOINT [ "python3" ]
# CMD [ "app.py"]
