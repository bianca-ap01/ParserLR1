# Fase de build (Vite/React)
FROM node:20 AS build
WORKDIR /app

# Instala deps
COPY lr1_app/frontend/package*.json ./
RUN npm ci

# Copia el código y construye
COPY lr1_app/frontend/ ./

# En el build inyectamos la URL base del API (por defecto /api porque nginx proxyea)
ARG VITE_API_BASE=/api
ENV VITE_API_BASE=${VITE_API_BASE}
RUN npm run build

# Fase de serve (nginx)
FROM nginx:alpine
# Config nginx SPA + proxy /api -> backend:8000 (see nginx.conf)
COPY deploy/nginx.conf /etc/nginx/conf.d/default.conf
# Copia los estáticos construidos
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80