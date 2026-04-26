# IMPORTANT: build context must be the repo root, not this directory.
#   docker build -f frontend/portal-admin/Dockerfile -t portal-admin:dev .

FROM node:20-alpine AS build
WORKDIR /app

COPY tailwind.config.cjs /tailwind.config.cjs
COPY design-system /design-system

COPY frontend/portal-admin/package*.json ./
RUN npm ci --no-audit --no-fund

COPY frontend/portal-admin/ ./
RUN npm run build -- --configuration=production

FROM nginx:1.27-alpine
COPY frontend/portal-admin/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist/portal-admin/browser /usr/share/nginx/html

EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
