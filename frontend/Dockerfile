FROM node:20-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install --legacy-peer-deps

# Copy app files
COPY . .

# Expose port
EXPOSE 3000

# Start dev server
CMD ["npm", "start"]
