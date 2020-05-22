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
### Routing not working on Windows/macOS with Docker Desktop Kubernetes implementation
Windows and macOS both need an ingress if they're using the built-in Kubernetes context bundled with Docker Desktop, so we'll apply the "official" one:
```console
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-0.32.0/deploy/static/provider/cloud/deploy.yaml
```
According to `ingress-nginx` documentation: _"The first time the ingress controller starts, two [Jobs](https://kubernetes.io/docs/concepts/workloads/controllers/jobs-run-to-completion/) create the SSL Certificate used by the admission webhook. For this reason, there is an initial delay of up to two minutes until it is possible to create and validate Ingress definitions."_. That's why we must wait until those jobs are done:
```console
kubectl wait --namespace ingress-nginx --for=condition=ready pod --selector=app.kubernetes.io/component=controller --timeout=90s
```
If TLS certificate error appears while applying k8s YAML file after waiting for the certificate creation, it's because it's something wrong and there's no certificate (or a valid one), so, for testing purposes, it's possible to remove the webhook validator (obviously not recommended in production where a valid certificate is mandatory):
```console
kubectl delete validatingwebhookconfiguration ingress-nginx-admission
```
Now should be possible to apply with no trouble.
### Routing not working on Linux OSes
If you previously followed my instructions to install MicroK8s, there should be no problem while routing, however, you may missed to enable the ingress addon built-in this Kubernetes implementation. To ensure all addons are already enabled, please execute the following command:
```console
sudo microk8s enable dns dashboard registry ingress
```
That's all! Now should be possible to apply the YAML file.