FROM python:3.6.12-alpine3.12

COPY . .

RUN apk update && apk add py3-libxml2

RUN pip install -r requirements.txt

RUN echo $GMAIL_PASS > app_pass.txt

ENTRYPOINT ["python", "./detector.py", "$FROM_EMAIL", "$TO_EMAILS"]
