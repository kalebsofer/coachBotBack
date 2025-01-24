# Monitoring Service

The monitoring service provides observability for the Coach Bot system using Prometheus, Grafana, and Loki. It enables metrics collection, visualization, and log aggregation.

## Core Components

### Prometheus
- Time-series database for metrics collection
- Scrapes metrics from configured endpoints
- Provides alerting capabilities
- Stores data for analysis and visualization

### Grafana
- Visualization tool for metrics and logs
- Dashboards for real-time monitoring
- Alerting and notification integration

### Loki
- Log aggregation system
- Integrates with Grafana for log visualization
- Supports structured and unstructured logs
- Efficient storage and retrieval

## Development

### Prerequisites
- Docker and Docker Compose
- Access to the Coach Bot network


### Running the Monitoring Stack
```bash
# Start monitoring services
docker-compose up -d prometheus grafana loki

# View logs
docker-compose logs -f prometheus grafana loki
```

## Configuration

### Prometheus
- Configuration file: `prometheus.yml`
- Scrape intervals and targets
- Alerting rules

### Grafana
- Provisioning: Dashboards and data sources
- User authentication and permissions
- Alert channels and notifications

### Loki
- Configuration file: `loki-config.yml`
- Log retention and storage settings
- Query capabilities

## Usage

### Accessing Grafana
- URL: `http://localhost:3000`
- Default credentials: `admin/admin`
- Configure dashboards and alerts

### Querying Logs with Loki
- Use Grafana's Explore feature
- Filter logs by labels and time range
- Combine with metrics for comprehensive insights

### Monitoring Metrics with Prometheus
- Access Prometheus UI: `http://localhost:9090`
- Query metrics using PromQL
- Set up alerts for critical conditions

## Troubleshooting

### Common Issues
- Ensure all services are running: `docker-compose ps`
- Check logs for errors: `docker-compose logs -f`
- Verify network connectivity between services

### Logs and Metrics Not Appearing
- Check scrape targets in Prometheus
- Verify data source configuration in Grafana
- Ensure Loki is receiving logs from sources

## Additional Resources
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Loki Documentation](https://grafana.com/docs/loki/latest/)
