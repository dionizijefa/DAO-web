FROM ubuntu as intermediate
#ARG GITHUB_TOKEN=${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}
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git && \
    apt install -y nodejs &&  \
    npm install -y @angular/cli

RUN git clone https://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@github.com/dionizijefa/DAO-web

RUN ng build --prod
