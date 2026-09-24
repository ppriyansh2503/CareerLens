FROM node:20-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 3000

# Simple nginx configuration
RUN echo 'server { \
    listen 3000; \
    location / { \
        root /usr/share/nginx/html; \
        index index.html index.htm; \
        try_files $uri $uri/ /index.html; \
    } \
    location /api { \
        proxy_pass http://backend:8000; \
    } \
    location /uploads { \
        proxy_pass http://backend:8000; \
    } \
}' > /etc/nginx/conf.d/default.conf

CMD ["nginx", "-g", "daemon off;"]
