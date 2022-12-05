FROM python:3

ARG VERSION_APP
ARG TAG_APP
ENV VERSION=$VERSION_APP
ENV TAG=$TAG_APP
WORKDIR /usr/src/github_app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src/main.py .
COPY scripts/init.sh .
RUN chmod +x ./init.sh
CMD python ./main.py && cat outputs/*.csv
