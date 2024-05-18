FROM python:3.11-slim

WORKDIR /app

ENV VIRTUAL_ENV=/home/packages/.venv

RUN pip install -U pip uv
COPY requirements.lock .
RUN uv venv /home/packages/.venv && uv pip install --no-cache -r requirements.lock

ENV PATH="/home/packages/.venv/bin:$PATH"

COPY . .

CMD [ "uvicorn", "app:app", "--port", "8002", "--host", "0.0.0.0" ]
