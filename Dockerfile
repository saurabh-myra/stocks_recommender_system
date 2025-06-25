FROM --platform=${TARGETPLATFORM:-linux/amd64} python:3.8-slim-buster

WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5050

EXPOSE 5050

ENTRYPOINT ["python3"]
CMD ["-m", "flask", "run"]
