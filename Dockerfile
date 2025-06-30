FROM pytorch/pytorch:2.3.0-cuda12.1-cudnn8-runtime

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

EXPOSE 8000

ENTRYPOINT ["chainlit", "run", "app.py", "--host", "0.0.0.0", "--port", "8000"]