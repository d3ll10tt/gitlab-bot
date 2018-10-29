from python:3.7.1-alpine3.8

ADD context/gitlab-bot /src
WORKDIR /src
RUN pip install -r requirements.txt
CMD python ./gitlab-bot.py

