FROM epicwynn/pd-base

ARG GMAIL_PASS

ENV GMAIL_PASS=${GMAIL_PASS}

COPY . .

RUN echo $GMAIL_PASS > app_pass.txt

ENTRYPOINT ["./entrypoint.sh"]
