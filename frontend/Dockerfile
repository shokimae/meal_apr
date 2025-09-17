
FROM node:20-alpine

WORKDIR /app

# Install deps based on lockfiles if present
COPY package*.json ./
RUN if [ -f package-lock.json ]; then npm ci;     elif [ -f yarn.lock ]; then yarn install;     elif [ -f pnpm-lock.yaml ]; then npm i -g pnpm && pnpm i;     else npm i; fi

# Copy the rest of the app
COPY . .

EXPOSE 3000
CMD ["npm", "run", "dev"]
