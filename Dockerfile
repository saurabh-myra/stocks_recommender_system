FROM --platform=${TARGETPLATFORM:-linux/amd64} python:3.8-slim-buster

WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt

ENV FLASK_APP=app.py
ENV PORT=5050

# ✅ Expose the correct internal port
EXPOSE 5050

ENTRYPOINT ["python3"]
CMD ["-m", "flask", "run", "--host=0.0.0.0", "--port=5050"]
