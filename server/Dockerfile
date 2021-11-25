FROM continuumio/anaconda3

MAINTAINER Dionizije Fa "dionizije.fa@hotmail.com"

ENV PYTHONUNBUFFERED 1

RUN mkdir -p /usr/src/app

WORKDIR /usr/src/app

ADD environment.yml /usr/src/app/

RUN conda env create -f environment.yml

RUN echo "source activate $(head -1 environment.yml | cut -d' ' -f2)" > ~/.bashrc

ENV PATH /opt/conda/envs/$(head -1 environment.yml | cut -d' ' -f2)/bin:$PATH

RUN conda init

ADD ./main/uwsgi.ini /etc/uwsgi.ini

EXPOSE 5000

CMD ["conda", "run", "dao_web", "pip", "install", "shap"]

CMD ["conda", "run", "-n", "dao_web", "uwsgi", "--ini", "/etc/uwsgi.ini"]
