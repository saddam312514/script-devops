# start by pulling the python image
FROM python:3.8-slim-buster
# copy the requirements file into the image
COPY ./requirements.txt /app/requirements.txt

# switch working directory
WORKDIR /app

RUN apt-get update
RUN apt install snapd -y
RUN apt-get install -y ca-certificates wget
RUN apt-get install curl -y
RUN snap install redis || true

RUN apt-get update
RUN systemctl unmask snapd.service
RUN systemctl enable snapd.service
RUN systemctl start snapd.service; exit 0
# install the dependencies and packages in the requirements file
RUN pip install -r requirements.txt

# copy every content from the local file to the image
COPY . /app

# configure the container to run in an executed manner
ENTRYPOINT [ "python" ]

CMD ["main.py" ]
