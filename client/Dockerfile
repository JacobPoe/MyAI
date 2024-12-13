FROM node:20
WORKDIR /app

COPY . ./
RUN npm ci && npm run build

# Install an HTTP server to serve the static files
RUN npm install -g serve

# Run the app on port
CMD ["serve", "-s", "dist", "-l", "8080"]

# Expose port 8080
EXPOSE 8080