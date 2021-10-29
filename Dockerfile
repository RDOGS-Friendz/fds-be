FROM python:3.9
COPY . /app
WORKDIR /app
RUN mkdir log
RUN pip install -r requirements.txt
RUN pip install uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
