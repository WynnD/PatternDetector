FROM epicwynn/pd-base:latest

COPY . .

ENTRYPOINT ["./entrypoint.sh"]
