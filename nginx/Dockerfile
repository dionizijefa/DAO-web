FROM nginx:alpine

MAINTAINER Dionizije Fa "dionizije.fa@hotmail.com"

# Copy custom nginx config
COPY ./nginx/nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

ENTRYPOINT ["nginx"]
CMD ["-g", "daemon off;"]
