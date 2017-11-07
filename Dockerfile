FROM python:3.5
RUN mkdir /Dorm
COPY ./requirements.txt /Dorm/
WORKDIR /Dorm
RUN pip install -r requirements.txt
COPY ./dorm /Dorm/dorm
COPY ./service.py /Dorm/
COPY ./app.py /Dorm/
EXPOSE 1307
# CMD ["/usr/lib/postgresql/9.3/bin/postgres", "-D", "/var/lib/postgresql/9.3/main", "-c", "config_file=/etc/postgresql/9.3/main/postgresql.conf"]
CMD ["ipython", "-i", "app.py"]
