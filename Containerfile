FROM python:3.7-slim
COPY . /app
WORKDIR /app
RUN pip install .
CMD ["ava_chatbot_backend_service"]
