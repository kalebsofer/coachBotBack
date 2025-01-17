FROM grafana/grafana:10.0.0

COPY src/monitoring/grafana/provisioning /etc/grafana/provisioning

ENV GF_SECURITY_ADMIN_USER=admin
ENV GF_SECURITY_ADMIN_PASSWORD=admin
ENV GF_USERS_ALLOW_SIGN_UP=false 