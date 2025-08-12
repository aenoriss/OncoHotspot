# Multi-stage build for OncoHotspot
FROM node:18-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM node:18-alpine AS backend-build
WORKDIR /app/backend
COPY backend/package*.json ./
RUN npm ci
COPY backend/ ./
RUN npm run build

FROM node:18-alpine
WORKDIR /app
RUN apk add --no-cache sqlite
COPY --from=backend-build /app/backend/dist ./backend/dist
COPY --from=backend-build /app/backend/node_modules ./backend/node_modules
COPY --from=frontend-build /app/frontend/build ./frontend/build
COPY backend/package.json ./backend/
COPY database/ ./database/
EXPOSE 3001
CMD ["node", "backend/dist/index.js"]