FROM python:3.8

# RUN apt-get update && DEBIAN_FRONTEND=noninteractive \
# && apt-get upgrade -y
# RUN apt-get install -y python3  \
# && apt-get install -y python3-pip
RUN pip3 install Flask-API \
&& pip3 install flask_cors \
&& pip3 install requests



COPY . /app
WORKDIR /app
RUN python3 -m pip install --upgrade pip

RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3", "-u"]
CMD ["app.py"]
