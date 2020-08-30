FROM python:3.8-alpine

COPY . .

RUN mkdir -p /etc/apk && echo "http://dl-8.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories

RUN apk --no-cache --update add py3-numpy

ENV PYTHONPATH=/usr/lib/python3.8/site-packages

RUN grep -v "numpy" requirements.txt > requirements.txt

RUN pip install -r requirements.txt

RUN echo $GMAIL_PASS > app_pass.txt

ENTRYPOINT ["python", "./detector.py", "$FROM_EMAIL", "$TO_EMAILS"]
