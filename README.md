# Safran.AI DevOps internship technical challenge

## Context

You are provided with a brand new backend Python application with an API and a database. This application is deployed
using docker-compose.

You can build and run it locally as follows:

```bash
docker compose up --build
```

You can then access the API at https://fastapi.docker.localhost

```bash
curl -kX POST "https://fastapi.docker.localhost/datasets?name=my-dataset"

curl -kX GET "https://fastapi.docker.localhost/datasets"

curl -kX POST "https://fastapi.docker.localhost/datasets/1/reticulate"
```

## Your mission

This application is about to be deployed in production, but before that we would like to add some observability
to it. This will allow us to monitor the application's health and usage, and be alerted in case of any issue.

Your goal is to add observability to the application. You are free to modify any of the provided code
(API, docker-compose), but you must not change the application's behavior.

1. List the metrics that you find interesting to monitor, and why.

| **Metric**        | **Why?**                                        |
| ----------------- | ----------------------------------------------- |
| Request Count     | Understand app usage                            |
| Request Duration  | Detect performance issue                        |
| 5xx Error         | Detect server-side application issues           |
| DB Query Duration | Detect slow or inefficient database queries     |
| CPU Usage         | Detect CPU issue                                |
| Memory Usage      | Spot memory leaks or high memory usage          |
| App Uptime        | Ensure the application is running and available |

2. Add the necessary code and/or services to collect these metrics (we have included a few pointers to the documentation
   of popular tools, but feel free to use any other tool you find relevant).  
   Service Added: Prometheus, OpenTelemetry, Loki, Node-exporter

3. Add the necessary code and/or services to visualize these metrics.  
   Service Added: Grafana and Jaeger

## Appendix: Tool documentation

- [Prometheus](https://prometheus.io/docs/introduction/overview/)
- [Grafana](https://grafana.com/docs/grafana/latest/)
- [Traefik](https://doc.traefik.io/traefik/)
- [OpenTelemetry](https://opentelemetry.io/docs/)
- [Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)
