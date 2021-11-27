FROM continuumio/miniconda3
#FROM continuumio/anaconda3

MAINTAINER Dionizije Fa "dionizije.fa@hotmail.com"

ENV PYTHONUNBUFFERED 0

RUN mkdir -p /usr/src/app

WORKDIR /usr/src/app

COPY . /usr/src/app/

#RUN apt-get update && apt-get upgrade -y && apt-get install -y g++

RUN apt-get update && apt-get upgrade -y && apt-get install -y build-essential

RUN conda env create -f environment.yml  \
    && pip install shap==0.38.1

SHELL ["conda", "run", "-n", "dao_web", "/bin/bash", "-c"]

#ENV PATH /opt/conda/envs/$(head -1 environment.yml | cut -d' ' -f2)/bin:$PATH

#ENTRYPOINT ["uwsgi", "--ini", "/etc/uwsgi.ini"]

COPY uwsgi.ini /etc/uwsgi.ini

EXPOSE 5000

ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "dao_web", "uwsgi", "--ini", "/etc/uwsgi.ini"]
