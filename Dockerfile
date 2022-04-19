FROM python:3.7
WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8040
COPY . .
CMD python3 app.py  