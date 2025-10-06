# Smart Traffic Control System - Docker Configuration
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    cron \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p logs models static templates scripts

# Make scripts executable
RUN chmod +x scripts/*.py scripts/*.sh

# Create cron job file
RUN echo "*/5 * * * * cd /app && python3 scripts/data_collector.py >> logs/cron.log 2>&1" > /etc/cron.d/traffic-cron && \
    echo "*/15 * * * * cd /app && python3 scripts/ml_predictor.py >> logs/cron.log 2>&1" >> /etc/cron.d/traffic-cron && \
    echo "0 * * * * cd /app && python3 scripts/health_check.py >> logs/cron.log 2>&1" >> /etc/cron.d/traffic-cron && \
    echo "0 3 * * * cd /app && scripts/rotate_logs.sh >> logs/cron.log 2>&1" >> /etc/cron.d/traffic-cron

# Set permissions for cron
RUN chmod 0644 /etc/cron.d/traffic-cron && \
    crontab /etc/cron.d/traffic-cron

# Expose port
EXPOSE 5000

# Create startup script
RUN echo '#!/bin/bash\n\
# Start cron daemon\n\
cron\n\
\n\
# Initialize database and train model\n\
python3 -c "from app import init_db, predictor; init_db(); predictor.train_model()"\n\
\n\
# Start Flask application\n\
python3 app.py' > /app/start.sh && chmod +x /app/start.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/current-traffic || exit 1

# Start the application
CMD ["/app/start.sh"]