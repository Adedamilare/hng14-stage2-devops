FROM node:18-alpine AS build

WORKDIR /app
COPY package*.json .
RUN npm install

COPY . .
RUN npm run build

FROM node:18-alpine

RUN adduser -D appuser

WORKDIR /app
COPY --from=build /app .

USER appuser

EXPOSE 3000

HEALTHCHECK CMD wget --spider http://localhost:3000 || exit 1

CMD ["npm", "start"]