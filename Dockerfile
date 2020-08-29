FROM python:3.6.12-alpine3.12

RUN echo $GMAIL_PASS > app_pass.txt

ENTRYPOINT ["python", "./detector.py", "$FROM_EMAIL", "$TO_EMAILS"]
