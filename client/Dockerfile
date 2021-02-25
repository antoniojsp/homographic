FROM python:3.8

# RUN apt-get update && DEBIAN_FRONTEND=noninteractive  \
# && apt-get upgrade  -y
# RUN apt-get install -y python3  \
# && apt-get install -y python3-pip  \
# && apt-get install -y libgmp3-dev  \
# && apt-get install -y  libmpfr-dev libmpfr-doc libmpfr4 libmpfr4-dbg \
# && apt-get install -y libmpc-dev
RUN pip3 install phe \
&& pip3 install Flask-API \
&& pip3 install flask_cors \
&& pip3 install requests

COPY . /app
WORKDIR /app
RUN python3 -m pip install --upgrade pip

RUN pip3 install -r requirements.txt


ENTRYPOINT ["python3", "-u"]
CMD ["client.py"]
