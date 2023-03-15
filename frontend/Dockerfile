# build env
FROM node:13.12.0-alpine as build
WORKDIR /app
COPY package*.json ./
RUN sudo npm install
COPY . ./
RUN sudo npm run build
CMD cp -r build result_build
