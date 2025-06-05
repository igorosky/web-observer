FROM node:20-alpine AS build
WORKDIR /nm-frontend
COPY package*.json ./
RUN npm ci
COPY . ./
RUN npm run build_prod

FROM node:20-alpine
WORKDIR /nm-frontend
COPY --from=build /nm-frontend/dist/nm-frontend/ ./
CMD node server/server.mjs
EXPOSE 4000
