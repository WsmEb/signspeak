# ── Serve the single HTML file with nginx:alpine (~8 MB) ─────────────────────
FROM nginx:1.27-alpine

# Remove the default nginx page
RUN rm -rf /usr/share/nginx/html/*

# Copy our single-file app
COPY index.html /usr/share/nginx/html/index.html

# Custom nginx config:
#  - Serve on port 80
#  - Correct MIME types for the HTML
#  - Security headers
#  - Gzip for faster load
RUN printf 'server {\n\
    listen 80;\n\
    server_name _;\n\
    root /usr/share/nginx/html;\n\
    index index.html;\n\
\n\
    gzip on;\n\
    gzip_types text/html text/css application/javascript;\n\
\n\
    # Security headers\n\
    add_header X-Frame-Options "SAMEORIGIN";\n\
    add_header X-Content-Type-Options "nosniff";\n\
    # Allow camera access from the page itself\n\
    add_header Permissions-Policy "camera=self";\n\
\n\
    location / {\n\
        try_files $uri $uri/ /index.html;\n\
    }\n\
}\n' > /etc/nginx/conf.d/default.conf

EXPOSE 80
