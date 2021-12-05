FROM node:14.17.3-stretch-slim

WORKDIR /app

COPY package.json ./

RUN npm install -g @angular/cli

RUN npm install

COPY .  .

RUN ng build --prod

COPY /app/dist/ /usr/share/nginx/html
