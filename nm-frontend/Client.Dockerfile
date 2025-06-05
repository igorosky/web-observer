FROM node:20-alpine as build
RUN mkdir -p /app
WORKDIR /app
COPY package*.json /app/
RUN npm ci
COPY . /app
EXPOSE 4000/tcp
RUN npm run build_prod
CMD ["npm", "start", "--", "--host", "0.0.0.0", "--port", "4000"]
