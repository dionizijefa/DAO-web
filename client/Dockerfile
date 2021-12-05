FROM node:14.17.3-stretch-slim

WORKDIR /app
COPY package.json /app/

RUN npm install -g @angular/cli@11.0.4

RUN cd /app && npm install

COPY .  /app

RUN cd /app && ng build --prod

COPY /app/dist /usr/share/nginx/html
