FROM prom/prometheus:latest

COPY src/monitoring/prometheus/prometheus.yml /etc/prometheus/

USER root

RUN mkdir -p /prometheus && \
    addgroup -S prometheus && \
    adduser -S -G prometheus prometheus && \
    chown -R prometheus:prometheus /prometheus && \
    chmod 777 /prometheus

RUN chown prometheus:prometheus /etc/prometheus/prometheus.yml

USER prometheus

EXPOSE 9090

ENTRYPOINT [ "/bin/prometheus" ]
CMD [ "--config.file=/etc/prometheus/prometheus.yml", \
    "--storage.tsdb.path=/prometheus", \
    "--web.console.libraries=/usr/share/prometheus/console_libraries", \
    "--web.console.templates=/usr/share/prometheus/consoles" ] 