FROM python:3.9

ENV TZ=Europe/Moscow

ARG SSH_PRIVATE_KEY
ARG SSH_PUBLIC_KEY

RUN mkdir -p /root/.ssh && \
    chmod 0700 /root/.ssh && \
    ssh-keyscan bitbucket.org > /root/.ssh/known_hosts

RUN echo "${SSH_PRIVATE_KEY}" > /root/.ssh/id_rsa && \
    echo "${SSH_PUBLIC_KEY}" > /root/.ssh/id_rsa.pub && \
    chmod 600 /root/.ssh/id_rsa && \
    chmod 600 /root/.ssh/id_rsa.pub

RUN mkdir /executor


COPY entrypoint.sh /executor/entrypoint.sh
COPY requirements.txt /executor/requirements.txt

RUN apt-get update --allow-releaseinfo-change \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y locales \
 && sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen \
 && dpkg-reconfigure --frontend=noninteractive locales \
 && update-locale LANG=en_US.UTF-8

RUN pip install -r /executor/requirements.txt


ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8

RUN rm -rf /root/.ssh

WORKDIR /executor

CMD ["./entrypoint.sh"]
