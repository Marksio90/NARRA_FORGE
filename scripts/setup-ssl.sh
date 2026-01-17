#!/bin/bash
# NARRA_FORGE V2 SSL/TLS Setup Script (Let's Encrypt)

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
DOMAIN=$1
EMAIL=$2

if [ -z "$DOMAIN" ] || [ -z "$EMAIL" ]; then
    echo -e "${RED}Error: Domain and email are required${NC}"
    echo "Usage: $0 <domain> <email>"
    echo "Example: $0 narraforge.com admin@narraforge.com"
    exit 1
fi

echo -e "${GREEN}=== SSL/TLS Setup with Let's Encrypt ===${NC}"
echo "Domain: $DOMAIN"
echo "Email: $EMAIL"
echo ""

# Install certbot if not present
if ! command -v certbot &> /dev/null; then
    echo -e "${YELLOW}Installing certbot...${NC}"
    sudo apt-get update
    sudo apt-get install -y certbot python3-certbot-nginx
fi

# Create SSL directory
mkdir -p nginx/ssl

# Stop nginx if running
echo -e "${YELLOW}Stopping nginx...${NC}"
docker-compose -f docker-compose.prod.yml stop nginx || true

# Obtain certificate
echo -e "${YELLOW}Obtaining SSL certificate from Let's Encrypt...${NC}"
sudo certbot certonly --standalone \
    --preferred-challenges http \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN

# Copy certificates to nginx directory
echo -e "${YELLOW}Copying certificates...${NC}"
sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem nginx/ssl/key.pem
sudo chmod 644 nginx/ssl/cert.pem
sudo chmod 600 nginx/ssl/key.pem

# Create renewal script
cat > scripts/renew-ssl.sh <<RENEW_EOF
#!/bin/bash
# Auto-renew SSL certificates

set -e

echo "Renewing SSL certificates..."
docker-compose -f docker-compose.prod.yml stop nginx
sudo certbot renew
sudo cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/$DOMAIN/privkey.pem nginx/ssl/key.pem
docker-compose -f docker-compose.prod.yml start nginx
echo "SSL certificates renewed successfully"
RENEW_EOF

chmod +x scripts/renew-ssl.sh

# Setup automatic renewal (cron job)
echo -e "${YELLOW}Setting up automatic renewal...${NC}"
CRON_CMD="0 0 1 * * cd $(pwd) && ./scripts/renew-ssl.sh >> /var/log/ssl-renewal.log 2>&1"
(crontab -l 2>/dev/null | grep -v "renew-ssl.sh"; echo "$CRON_CMD") | crontab -

# Restart nginx
echo -e "${YELLOW}Starting nginx with SSL...${NC}"
docker-compose -f docker-compose.prod.yml start nginx

echo ""
echo -e "${GREEN}=== SSL/TLS Setup Complete ===${NC}"
echo "Certificates installed for: $DOMAIN"
echo "Certificate location: nginx/ssl/"
echo "Auto-renewal: Enabled (runs monthly)"
echo ""
echo "Test your SSL: https://www.ssllabs.com/ssltest/analyze.html?d=$DOMAIN"
