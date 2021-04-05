FROM python:slim-buster

EXPOSE 5000

COPY . /dzdp
WORKDIR /dzdp

RUN pip install -r requirements.txt

RUN useradd dzdp && chown -R dzdp /dzdp
USER dzdp

CMD ["sh", "start.sh"]
