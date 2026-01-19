# Frontend Dockerfile for NARRA_FORGE V2
# Automatic TypeScript type generation from OpenAPI spec
# Build context: project root (not frontend/)

FROM node:20-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app/frontend

# Copy package files
COPY frontend/package.json frontend/package-lock.json* ./

# Install dependencies
RUN if [ -f package-lock.json ]; then npm ci; else npm install && npm install --package-lock-only; fi


# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app/frontend

# Copy dependencies from deps stage
COPY --from=deps /app/frontend/node_modules ./node_modules

# Copy api-spec.json from root for type generation
COPY api-spec.json ../api-spec.json

# Copy application code
COPY frontend/ ./

# Set environment variables for build
ENV NEXT_TELEMETRY_DISABLED=1

# Generate TypeScript types from OpenAPI spec
RUN echo "Generating TypeScript types from OpenAPI spec..." && \
    npm run generate:types:local || echo "Warning: Type generation failed, using existing types"

# Build Next.js application
# The prebuild hook automatically runs type-check
RUN npm run build


# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Create non-root user
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy public folder if it exists (optional in Next.js)
# Note: This project doesn't use a public folder, so this line is commented out
# COPY --from=builder /app/frontend/public ./public

# Set the correct permission for prerender cache
RUN mkdir .next
RUN chown nextjs:nodejs .next

# Automatically leverage output traces to reduce image size
COPY --from=builder --chown=nextjs:nodejs /app/frontend/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/frontend/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000', (r) => {if (r.statusCode !== 200) throw new Error(r.statusCode)})"

# Run the application
CMD ["node", "server.js"]
