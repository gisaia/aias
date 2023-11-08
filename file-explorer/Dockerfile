### STAGE 1: Build ###

# We label our stage as 'builder'
FROM node:16.19.0 as builder
WORKDIR /app

COPY ./package.json  ./
COPY ./package-lock.json  ./

## installing necessary libraries
RUN npm install

COPY ./scripts/start.sh ./

COPY . .

## Build the angular app in production mode
RUN npm run build

### STAGE 2: Setup ###

FROM nginx:1.23.3-alpine
ARG version="latest"

LABEL io.arlas.wui-fam.version=${version}
LABEL vendor="Gisaïa"
LABEL description="This container build and serve the FAM-wui app"

RUN apk add --update bash jq netcat-openbsd curl && rm -rf /var/cache/apk/*

## Copy our default nginx config
COPY nginx/default.conf /etc/nginx/conf.d/

## Remove default nginx website
RUN rm -rf /usr/share/nginx/html/*

## From 'builder' stage copy over the artifacts in dist folder to default nginx public folder
COPY --from=builder /app/dist/file-explorer /usr/share/nginx/html
COPY --from=builder /app/start.sh /usr/share/nginx/

HEALTHCHECK CMD curl --fail http://localhost:80/ || exit 1

CMD /usr/share/nginx/start.sh
