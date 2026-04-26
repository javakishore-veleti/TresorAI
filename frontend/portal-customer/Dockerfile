# IMPORTANT: build context must be the repo root, not this directory.
#   docker build -f frontend/portal-customer/Dockerfile -t portal-customer:dev .
#
# That lets us COPY the shared root-level tailwind.config.cjs and design-system/
# (which the portal's own configs reference via ../../).

# Stage 1 — build the Angular bundle
FROM node:20-alpine AS build
WORKDIR /app

# Shared design tokens (placed at /tailwind.config.cjs and /design-system so the
# portal's relative paths ../../tailwind.config.cjs and ../../../design-system/tokens.css resolve)
COPY tailwind.config.cjs /tailwind.config.cjs
COPY design-system /design-system

# Portal sources
COPY frontend/portal-customer/package*.json ./
RUN npm ci --no-audit --no-fund

COPY frontend/portal-customer/ ./
RUN npm run build -- --configuration=production

# Stage 2 — serve the static bundle via nginx
FROM nginx:1.27-alpine
COPY frontend/portal-customer/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist/portal-customer/browser /usr/share/nginx/html

EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
