FROM python:3.6
RUN set -ex && python3.6 -m pip install pipenv --upgrade
RUN set -ex && mkdir /dorm
WORKDIR /dorm

COPY ./dorm /dorm
COPY ./Pipfile /dorm
RUN pipenv --three
RUN set -ex && pipenv install --skip-lock
CMD ["pipenv", "run", "python3"]
# start command
# docker run -it --network dorm_net -v /var/run/docker.sock:/var/run/docker.sock dorm_master
