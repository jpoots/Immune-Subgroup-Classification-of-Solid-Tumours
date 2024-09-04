# Dockerfile to define react frontend

FROM node:20.17-bullseye

# create working dir, set workdir
RUN mkdir /react-app
WORKDIR /react-app

COPY utils utils
COPY public public
COPY src src
COPY package-lock.json package-lock.json
COPY package.json package.json
COPY vite.config.js vite.config.js
COPY index.html index.html

RUN npm i 
RUN npm run build

EXPOSE 5173

CMD ["npm", "run", "preview"]