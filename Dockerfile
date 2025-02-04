FROM joyzoursky/python-chromedriver:latest

WORKDIR /app

COPY core/requirements.txt .
RUN pip install -r requirements.txt

COPY . .

