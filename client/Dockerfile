FROM node:14.17.3-stretch-slim AS build

WORKDIR /usr/src/client

COPY . .

RUN npm install -g @angular/cli \
    && npm install

RUN ng build --prod

RUN mkdir -p /usr/share/nginx/html

COPY --from=build /usr/src/client/dist /usr/share/nginx/html




