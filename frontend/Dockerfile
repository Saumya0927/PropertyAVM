FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy all source code
COPY . .

# Build the Next.js app
RUN npm run build

# Expose port
EXPOSE 3000

ENV NODE_ENV production
ENV PORT 3000

# Start the application
CMD ["npm", "start"]