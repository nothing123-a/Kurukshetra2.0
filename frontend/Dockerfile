# Stage 1: Build React + Vite app
FROM node:20-alpine AS build

WORKDIR /app

# Copy package manifests first for efficient Docker layer caching
COPY package*.json ./
RUN npm install

# Copy application source code
COPY . .

# Pass backend URL at build time (optional, default is empty to use Nginx proxy)
ARG VITE_API_BASE_URL=""
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

# Build the production bundle into /app/dist
RUN npm run build

# Stage 2: Lightweight production Nginx web server
FROM nginx:alpine

# Copy static assets from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy Nginx SPA reverse proxy configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
