# syntax=docker/dockerfile:1
# Build from repo root: docker compose build web

FROM node:20-alpine AS deps
WORKDIR /build/frontend
COPY frontend/package.json ./
RUN npm install

FROM node:20-alpine AS builder
WORKDIR /build
COPY branding.json branding.json
COPY assets ./frontend/public/assets
COPY frontend ./frontend
COPY --from=deps /build/frontend/node_modules ./frontend/node_modules
WORKDIR /build/frontend
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
RUN addgroup --system --gid 1001 nodejs && adduser --system --uid 1001 nextjs
COPY --from=builder /build/frontend/public ./public
COPY --from=builder --chown=nextjs:nodejs /build/frontend/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /build/frontend/.next/static ./.next/static
USER nextjs
EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME=0.0.0.0
CMD ["node", "server.js"]
