# 1. Build Stage
FROM node:18-alpine AS builder
WORKDIR /app

# Copy dependencies
COPY package*.json ./
RUN npm install

# Copy source
COPY . .

# Build SvelteKit
RUN npm run build

# 2. Production Stage
FROM node:18-alpine AS production
WORKDIR /app

# Copy only needed files
COPY package*.json ./
RUN npm ci --omit=dev

# Copy built output
COPY --from=builder /app/build ./build

EXPOSE 3000

# Jalankan server node
CMD ["node", "build"]
