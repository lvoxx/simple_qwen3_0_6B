FROM pytorch/pytorch:2.7.1-cuda11.8-cudnn9-runtime

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

EXPOSE 8000

ENTRYPOINT ["chainlit", "run", "app.py", "--host", "0.0.0.0", "--port", "8000"]