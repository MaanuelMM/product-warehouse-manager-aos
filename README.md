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