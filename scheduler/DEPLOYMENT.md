# Production Deployment Guide

## Prerequisites

- Docker & Docker Compose
- PostgreSQL 15+
- Python 3.9+
- Anthropic API Key
- SMTP/Email service configured

## Environment Setup

### 1. Clone Repository

```bash
git clone https://github.com/harshalnnpednekar/AI-DS-Summer-Internship-Agentic-AI.git
cd AI-DS-Summer-Internship-Agentic-AI
```

### 2. Create Environment Variables

```bash
cp scheduler/.env.example scheduler/.env
```

Edit `scheduler/.env`:

```
API_BASE_URL=http://backend:8000
SCHEDULER_INTERVAL_MINUTES=5
NOTIFICATION_WINDOW_DAYS=3
ANTHROPIC_API_KEY=your-api-key-here
LOG_LEVEL=INFO
MOCK_API_ENABLED=false
ENV=production
```

### 3. Database Setup

```bash
# Create .env for database
cat > .env << EOF
DB_USER=postgres
DB_PASSWORD=secure_password_here
DB_NAME=events_db
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
ANTHROPIC_API_KEY=your-anthropic-key
EOF
```

## Deployment Options

### Option 1: Docker Compose (Recommended)

```bash
docker-compose up -d
```

Verify services:

```bash
docker ps
docker-compose logs -f
```

### Option 2: Manual Installation

#### Install Python Dependencies

```bash
cd scheduler
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Run Scheduler

```bash
python main.py run
```

### Option 3: Systemd Service (Linux)

Create `/etc/systemd/system/scheduler.service`:

```ini
[Unit]
Description=Event Scheduler Service
After=network.target

[Service]
Type=simple
User=scheduler
WorkingDirectory=/opt/scheduler
ExecStart=/opt/scheduler/venv/bin/python main.py run
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable scheduler
sudo systemctl start scheduler
```

Monitor:

```bash
sudo systemctl status scheduler
sudo journalctl -u scheduler -f
```

## Monitoring & Logging

### Health Check

```bash
curl http://localhost:8001/health
```

### View Logs

Docker:
```bash
docker logs scheduler_agent -f
```

Systemd:
```bash
journalctl -u scheduler -f
```

### Metrics

Configure Prometheus:

```yaml
scrape_configs:
  - job_name: 'scheduler'
    static_configs:
      - targets: ['localhost:8001']
```

## Backup & Recovery

### Database Backup

```bash
docker exec postgres_db pg_dump \
  -U postgres events_db > backup.sql
```

### Database Restore

```bash
docker exec -i postgres_db psql \
  -U postgres events_db < backup.sql
```

## Troubleshooting

### Service won't start

Check logs:
```bash
docker logs scheduler_agent
```

Common issues:
- API_BASE_URL incorrect
- ANTHROPIC_API_KEY missing
- Backend not running

### High memory usage

Increase scheduler interval:
```
SCHEDULER_INTERVAL_MINUTES=10
```

### Database connection fails

Verify PostgreSQL is running:
```bash
docker ps | grep postgres
```

### API timeout

Check backend service:
```bash
curl http://backend:8000/health
```

## Performance Tuning

### Adjust Scheduler Interval

Longer intervals = lower CPU:
```
SCHEDULER_INTERVAL_MINUTES=10
```

### Connection Pooling

Update config.py for database connections:
```python
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40
```

### Batch Processing

Process multiple events at once:
```python
workflow.batch_process_events(events, students_map)
```

## Security Checklist

- [ ] ANTHROPIC_API_KEY is secure
- [ ] Database password is strong
- [ ] API_BASE_URL uses HTTPS in production
- [ ] Logs don't contain sensitive data
- [ ] Firewall restricts access to port 8001
- [ ] Regular database backups enabled
- [ ] SSL/TLS configured for API calls

## Scaling Considerations

### Horizontal Scaling

Deploy multiple scheduler instances with load balancer:

```yaml
scheduler_1:
  ...
scheduler_2:
  ...
scheduler_3:
  ...
```

Ensure idempotent operations.

### Vertical Scaling

Increase resources:
- CPU: 2 -> 4 cores
- Memory: 2GB -> 4GB
- Disk: Monitor logs growth

## Maintenance

### Daily

- Monitor logs for errors
- Check scheduler job status
- Verify API connectivity

### Weekly

- Review performance metrics
- Check disk usage
- Backup database

### Monthly

- Update dependencies
- Review and rotate logs
- Security audit

## Rollback Procedure

If deployment fails:

```bash
docker-compose down
git checkout previous-version
docker-compose up -d
```

Verify:
```bash
docker-compose logs -f scheduler
```

## Support

For issues:
1. Check logs: `docker logs scheduler_agent`
2. Verify configuration in `.env`
3. Test API connectivity
4. Review GitHub issues
5. Contact team lead

## Useful Commands

```bash
docker-compose up -d
docker-compose down
docker-compose restart scheduler
docker-compose logs scheduler -f
docker ps
docker exec scheduler_agent python main.py status
docker-compose exec postgres_db psql -U postgres -d events_db
```
