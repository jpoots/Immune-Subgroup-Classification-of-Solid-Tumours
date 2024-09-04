# Dockerfile to define react frontend

# python image
FROM node:20.17-bullseye

# create working dir, set workdir
RUN mkdir /react-app
WORKDIR /react-app

# set up software
COPY . .
RUN npm i 
RUN npm run build

EXPOSE 5173

CMD ["npm", "run", "preview"]