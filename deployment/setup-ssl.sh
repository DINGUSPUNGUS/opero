#!/bin/bash
# SSL Certificate Setup with Let's Encrypt

set -e

# Configuration
DOMAIN="yourdomain.com"
EMAIL="your-email@example.com"
NGINX_CONFIG="/etc/nginx/sites-available/opero"
SSL_DIR="/etc/nginx/ssl"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🔐 Setting up SSL certificates for Opero${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ Please run as root (use sudo)${NC}"
    exit 1
fi

# Install Certbot
echo -e "${YELLOW}📦 Installing Certbot...${NC}"
apt update
apt install -y certbot python3-certbot-nginx

# Create SSL directory
mkdir -p ${SSL_DIR}

# Stop nginx temporarily
echo -e "${YELLOW}⏸️ Stopping nginx...${NC}"
systemctl stop nginx

# Obtain certificate
echo -e "${YELLOW}🔐 Obtaining SSL certificate...${NC}"
certbot certonly \
    --standalone \
    --preferred-challenges http \
    --email ${EMAIL} \
    --agree-tos \
    --no-eff-email \
    -d ${DOMAIN} \
    -d www.${DOMAIN} \
    -d api.${DOMAIN}

# Copy certificates to nginx SSL directory
echo -e "${YELLOW}📄 Setting up certificate files...${NC}"
cp /etc/letsencrypt/live/${DOMAIN}/fullchain.pem ${SSL_DIR}/
cp /etc/letsencrypt/live/${DOMAIN}/privkey.pem ${SSL_DIR}/

# Set proper permissions
chown root:root ${SSL_DIR}/*
chmod 644 ${SSL_DIR}/fullchain.pem
chmod 600 ${SSL_DIR}/privkey.pem

# Create certificate renewal script
cat > /etc/cron.d/certbot-renewal << EOF
# Renew Let's Encrypt certificates
0 3 * * * root certbot renew --quiet --post-hook "systemctl reload nginx"
EOF

# Start nginx
echo -e "${YELLOW}▶️ Starting nginx...${NC}"
systemctl start nginx
systemctl enable nginx

# Test SSL configuration
echo -e "${YELLOW}🧪 Testing SSL configuration...${NC}"
nginx -t

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ SSL setup completed successfully!${NC}"
    echo -e "${YELLOW}📋 Certificate locations:${NC}"
    echo "  Full chain: ${SSL_DIR}/fullchain.pem"
    echo "  Private key: ${SSL_DIR}/privkey.pem"
    echo -e "${YELLOW}🔄 Auto-renewal configured via cron${NC}"
    echo -e "${YELLOW}🌐 Your site should now be accessible at:${NC}"
    echo "  https://${DOMAIN}"
    echo "  https://www.${DOMAIN}"
    echo "  https://api.${DOMAIN}"
else
    echo -e "${RED}❌ Nginx configuration test failed${NC}"
    exit 1
fi

# Test certificate
echo -e "${YELLOW}🧪 Testing certificate...${NC}"
certbot certificates

echo -e "${GREEN}🎉 SSL setup complete! Your Opero platform is now secure.${NC}"
