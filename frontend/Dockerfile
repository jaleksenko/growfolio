# frontend/Dockerfile
# Stage 1: Build the React app with Vite
FROM node:18 AS builder

# Set the working directory inside the container to /app
WORKDIR /app

# Copy package.json and package-lock.json (if available) to install dependencies
COPY package.json ./

# Install the app dependencies
RUN npm install

# Copy the entire source code into the container
COPY . .

# Build the React app for production (Vite will output to /app/dist)
RUN npm run build

# Debug: List the contents of /app to ensure the dist folder was created
# RUN ls -la /app

# Stage 2: Serve the React app with Nginx
FROM nginx:alpine

# Copy the Vite build output from the previous stage to the Nginx html directory
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port 80 to allow access to the application
EXPOSE 80

# Start Nginx in the foreground
CMD ["nginx", "-g", "daemon off;"]
