# product-warehouse-manager-aos
Product Warehouse Manager by using microservices and Kubernetes for AOS subject.

## Provisional
Build images placing in project's root path:
```console
docker build -t product-warehouse-manager-aos/invoicing-api -f .docker/invoicing-api/Dockerfile .
docker build -t product-warehouse-manager-aos/logging-api -f .docker/logging-api/Dockerfile .
docker build -t product-warehouse-manager-aos/orders-api -f .docker/orders-api/Dockerfile .
docker build -t product-warehouse-manager-aos/products-api -f .docker/products-api/Dockerfile .
docker build -t product-warehouse-manager-aos/swagger-ui -f .docker/swagger-ui/Dockerfile .
```
## Known issues and considerations
Windows and macOS need an ingress if they're using the built-in Kubernetes context bundled with Docker Desktop:
```console
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-0.32.0/deploy/static/provider/cloud/deploy.yaml
```
If TLS certificate error appears while applying k8s YAML file, it's because there's no certificate (or a valid one), so, for testing purposes, it's possible to remove the webhook validator (obviously not recommended in production, only for testing purposes):
```console
kubectl delete validatingwebhookconfiguration ingress-nginx-admission
```
Now should be possible to apply with no trouble.