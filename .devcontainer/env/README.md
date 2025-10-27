# Environment Configuration

This directory contains environment variable configuration files for the devcontainer.

## Setup

The `.env` files are gitignored for security. You need to create them manually:

```bash
# Create netbox.env
cat > netbox.env << 'EOF'
ALLOWED_HOSTS=*
CORS_ORIGIN_ALLOW_ALL=true
DB_HOST=postgres
DB_NAME=netbox
DB_PASSWORD=your_secure_password_here
DB_USER=netbox
DEBUG=true
ENFORCE_GLOBAL_UNIQUE=true
LOGIN_REQUIRED=false
GRAPHQL_ENABLED=true
MAX_PAGE_SIZE=1000
MEDIA_ROOT=/opt/netbox/netbox/media
REDIS_DATABASE=0
REDIS_HOST=redis
REDIS_INSECURE_SKIP_TLS_VERIFY=false
REDIS_PASSWORD=your_secure_redis_password_here
SECRET_KEY=your_very_long_secret_key_here
SUPERUSER_API_TOKEN=0123456789abcdef0123456789abcdef01234567
SUPERUSER_EMAIL=admin@example.com
SUPERUSER_NAME=admin
SUPERUSER_PASSWORD=admin
STARTUP_SCRIPTS=false
WEBHOOKS_ENABLED=true
DEVELOPER_MODE=true
LANGUAGE_CODE=en-CA
ENABLE_LOCALIZATION=true
EOF

# Create postgres.env
cat > postgres.env << 'EOF'
POSTGRES_DB=netbox
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_USER=netbox
EOF

# Create redis.env
cat > redis.env << 'EOF'
REDIS_PASSWORD=your_secure_redis_password_here
EOF
```

**Note:** Make sure to use the same passwords in both `netbox.env` and `postgres.env` / `redis.env`.

## Security

- Never commit `.env` files to git
- Use strong, unique passwords for production environments
- The default credentials are for development only
