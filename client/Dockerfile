FROM node:14.17.3-stretch-slim as build

WORKDIR /usr/local/app

COPY ./ /usr/local/app/

RUN npm install -g @angular/cli

RUN npm install

COPY .  .

RUN ng build --prod


FROM nginx:alpine

MAINTAINER Dionizije Fa "dionizije.fa@hotmail.com"

# Copy custom nginx config
COPY ./nginx.conf /etc/nginx/nginx.conf

COPY --from=build /usr/local/app/dist/ /usr/share/nginx/html

EXPOSE 80

ENTRYPOINT ["nginx"]
CMD ["-g", "daemon off;"]

