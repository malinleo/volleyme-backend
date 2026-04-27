#!/bin/bash
# Remove unused Docker images and dangling build cache
# Add to crontab -e: 0 3 * * * /opt/volleyme/.ci/cleanup-images.sh >> /var/log/docker-cleanup.log 2>&1

echo "$(date '+%Y-%m-%d %H:%M:%S') Starting Docker cleanup..."

# Remove images not used by any container
docker image prune -af --filter "until=24h"

# Remove dangling build cache
docker builder prune -f --filter "until=24h"

echo "$(date '+%Y-%m-%d %H:%M:%S') Cleanup done."
