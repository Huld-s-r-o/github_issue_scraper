FROM python:3

ARG VERSION_APP
ENV VERSION=$VERSION_APP
WORKDIR /usr/src/github_app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod +x ./init.sh
CMD python ./main.py && cat outputs/*.csv
