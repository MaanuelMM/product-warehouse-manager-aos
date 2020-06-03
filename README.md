# Gestor de Almacén de Productos para la asignatura de AOS
Gestor de Almacén de Productos usando microservicios y Kubernetes para la asignatura de AOS.

## Objetivo
El principal objetivo de esta tarea consiste en consolidar los conceptos relacionados con la infraestructura y el despliegue de una aplicación que sigue una arquitectura orientada a servicios. La aplicación en cuestión es el **gestor de almacén de productos** sobre el que se ha trabajado en la primera práctica, en la cual cada grupo especificó una API para uno de los servicios de los que consta dicha aplicación. Para ello se estudiará y planificará la infraestructura necesaria para la integración de todos esos servicios, teniendo en cuenta que se plantean dos enfoques: un despliegue y puesta en marcha en un host con **Docker Compose** y un despliegue y puesta en marcha en un **cluster Kubernetes**.

## Enunciado
La consecución de este objetivo se planifica en las siguientes fases de complejidad incremental:
1. Memoria descriptiva con esquema de despliegue de los servicios, comunicaciones entre ellos, contenedores necesarios para cada uno de ellos y la justificación de todas las decisiones tomadas.
2. Ficheros necesarios para realizar el despliegue de todos los servicios de la aplicación con **Docker Compose**. (NOTA: Para que el objetivo se considere alcanzado, el despliegue debe funcionar por completo tras ejecutar el comando `docker-compose up`)
3. Reorganización de los contenedores y servicios para su despliegue en un cluster **Kubernetes**. (NOTA: Para que el objetivo se considere alcanzado, el despliegue debe funcionar por completo tras ejecutar el comando `kubectl apply -f <fichero>`)
4. Se valorará la simulación del comportamiento de los servicios mediante el empleo de herramientas de mocking tales como [Stoplight Prism](https://stoplight.io/open-source/prism/) y [Postman](https://www.postman.com/). (Opcional, sube nota)
5. Se valorará la implementación de la API del servicio que cada grupo especificó en la primera práctica. (Opcional, sube nota).

## Notas
- En el diseño de cada servicio se tendrá en cuenta que cada uno de los servicios deberá contar con su propio mecanismo de persistencia
- Se deberá enviar un único fichero comprimido en el que se adjuntarán todos los ficheros necesarios para desplegar el servicio asignado, tanto en **Docker Compose** como en **Kubernetes**. Obligatoriamente se incluirá un Fichero `README.md` que contendrá las instrucciones para realizar los despliegues de la aplicación, así como toda la información que se considere oportuna.
- Para realizar esta práctica se mantendrán los grupos de 3 alumnos definidos en la primera práctica. Aquellos alumnos que opten por evaluación solo por prueba final realizarán el ejercicio de manera individual.

## References to specifications
- Productos: https://github.com/RYSKZ/OpenAPI-Specification-Productos (recibido 05/05)
- Pedidos: https://github.com/santiagocarod/Especificacion-API-Pedidos (recibido 05/05)
- Eventos: https://github.com/MaanuelMM/logging-api-aos (recibido 04/05)
- Facturación: https://github.com/jorgegomezbueno/EspecificacionAOS (recibido 05/05)

## Implementación resultante
### Despliegue propuesto
#### Esquema de despliegue
![Esquema de despliegue](/docs/img/product-warehouse-manager-aos@3.125x.png)

#### Componentes y conexiones
- **API de Productos:** microservicio que maneja las peticiones HTTP a los endpoint `/Productos` y  `/Categorias` con los datos de la **BD de Almacén**.
- **API de Pedidos:** microservicio que maneja las peticiones HTTP al endpoint `/pedidos` con los datos de la **BD de Almacén**.
- **API de Facturación:** microservicio que maneja las peticiones HTTP a los endpoint `/Factura` y  `/Organizacion` con los datos de la **BD de Almacén**.
- **API de Eventos:** microservicio que maneja las peticiones HTTP al endpoint `/events` y almacena la información en la **BD de Eventos**.
- **API de Gestor de Almacén:** microservicio enrutador que recibirá cada petición HTTP de la API y lo redireccionará donde corresponda.
- **BD de Almacén:** microservicio de base de datos relacional que almacena los datos del almacén a nivel de negocio (productos, categorías, pedidos, facturas y organizaciones) producido por los correspondientes microservicios.
- **BD de Eventos:** microservicio de base de datos no relacional que almacena los datos de eventos de la API.

#### Réplicas
Acorde al esquema aportado, es posible producir más de una réplica de los microservicios de la primera práctica (`Productos`, `Pedidos`, `Fracturación` y `Eventos`) sin mayor inconveniente, pues tanto **Docker Compose** como **Kubernetes** lo realizan de forma transparente al resto de microservicios.

También se podría realizar réplicas de las bases de datos, sin embargo, habría que tratar el tema de la consistencia, en donde puede que nos haga falta un contenedor intermedario o no (hay contenedores que permiten gestionar esta inconsistencia con variables de entorno y autodescubrimiento).

## Despliegue realizado
### Docker-Compose
![Esquema Docker-Compose](/docs/img/product-warehouse-manager-aos-docker-compose@3.125x.png)
#### Justificación
A diferencia del despliegue propuesto, en este se hace uso de dos redes, una externa y otra interna, y la idea es **aislar a los microservicios del exterior** a través de un embajador que, a su vez, nos permite redirigir el tráfico que le llega por parte del router.

También cabe destacar que únicamente se ha llegado a implementar el servicio de `eventos` con su base de datos, mientras que el resto de servicios hacen uso de un mock server sin base de datos asociada.

### Kubernetes
![Esquema Docker-Compose](/docs/img/product-warehouse-manager-aos-kubernetes@3.125x.png)
#### Justificación
Aquí seremos menos ambiciosos, por tanto, usaremos un único router sin aislamiento de red. La razón detrás de ello es para usar el `ingress-nginx` de la gente de **Kubernetes**, el cual nos permitirá, al igual que en la implementación de **Docker-Compose**, enrutar a los microservicios correspondientes cada una de las peticiones HTTP recibidas.

### Información adicional
Los enrutados de ambas implementaciones siguen la siguiente especificación:
- `localhost` y `swagger.localhost`: permite la interacción con **Swagger UI**, en donde podrá manipular los microservicios desplegados.
- `api.localhost`: es la URL que te permitirá manipular los microservicios con los **/endpoints** correspondientes a cada uno de ellos.

### Interacción con el despliegue
**IMPORTANTE:** es obligatorio no tener ningún servicio en el sistema anfitrión ocupando los puertos 80 y 443, pues se hará uso de los mismos para desplegar el servicio; por tanto, se insta a parar dichos servicios para poder desplegar este.

#### Docker-Compose
Para desplegar con **Docker-Compose**, bastará con abrir una consola de comandos con los permisos suficientes como para poder ejecutar el binario `docker-compose`, ejecutando la siguiente línea de comando:

```console
docker-compose up -d
```

Al principio tardará en descargar las imágenes y crear los contenedores, pero una vez finalice, bastará con abrir el navegador y dirigirse a la URL `localhost` en donde podrá manipular el servicio a través de **Swagger UI**.

Una vez finalizada su interacción, podrá finalizar y eliminar lo desplegado con el siguiente comando:

```console
docker-compose down
```

#### Kubernetes

##### Requisitos previos
###### Windows y macOS
Para este supuesto, primero debemos activar la implementación **Kubernetes** proporcionada por **Docker** (no haremos uso de ninguna otra implementación tales como `minikube` o `microk8s` con **Multipass**).

Para ello debemos abrir las opciones de **Docker for Desktop** y activar la implementación de **Kubernetes**:


![Kubernetes from Docker Desktop](/docs/img/kubernetes-docker-desktop.png)

Una vez activado, deberemos desplegar `ingress-nginx` proporcionado por la gente de **Kubernetes** con el siguiente comando:

```console
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-0.32.0/deploy/static/provider/cloud/deploy.yaml
```

Una vez realizado este paso, para asegurarnos de que dicho despliegue se hace correctamente, debemos ejecutar el siguiente comando (tal y como se describe [aquí](https://kubernetes.github.io/ingress-nginx/deploy/)):

```console
kubectl wait --namespace ingress-nginx --for=condition=ready pod --selector=app.kubernetes.io/component=controller --timeout=90s
```

Si por algún casual, una vez hayamos desplegado una de las dos opciones (las cuales se encuentran descritas más abajo) no enruta a este, podemos eliminar el `webhook` que comprueba el certificado TLS con el siguiente comando:

```console
kubectl delete validatingwebhookconfiguration ingress-nginx-admission
```

Una vez acabemos con el despliegue, deberemos ejecutar el siguiente comando para eliminar el `ingress` y que no nos ocupe los puertos:

```console
kubectl delete -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-0.32.0/deploy/static/provider/cloud/deploy.yaml
```

Ya volveremos a tener los puertos 80 y 443 libres.

###### GNU\Linux
Para Linux haremos uso de `microk8s`, clúster de **Kubernetes** proporcionado por **Canonical**.

Como requisito previo necesitaremos del gestor de paquetes `snap`, el cuál se puede instalar [de esta foma](https://snapcraft.io/docs/installing-snapd) según cada distribución de Linux.

Una vez realizado dicho paso, para instalar `microk8s` ejecutaremos el siguiente comando:

```console
sudo snap install microk8s --classic
```

Esperaremos a que esté listo:

```console
microk8s status --wait-ready
```

Activaremos los servicios que nos interesan, y ya podremos desplegar la opción que queramos:

```console
microk8s enable dns ingress
```

Una vez terminado, podemos, o bien desactivar el `ingress`:

```console
microk8s disable ingress
```

O bien podemos parar el clúster:

```console
microk8s stop
```

De una forma u otra ya tendremos los puertos 80 y 443 libres.

**IMPORTANTE**: `microk8s` tiene embebido el ejecutable `kubectl`, y para su invocación, en vez de escribir directamente `kubectl`, deberemos escribir `microk8s.kubectl` seguido de lo que queramos realizar.

##### Opción 1: uso de volúmenes
Kubernetes no permite el uso de `paths` relativos, por lo que para desplegar esta opción debemos realizar un paso previo dependiendo del sistema operativo que estemos usando.

###### GNU\Linux
Bastará con abrir el fichero `k8s-volume.yaml` y cambiar en el **PersistentVolume** el `path` del `hostPath` con el path raíz del proyecto:

```yaml
hostPath:
    path: /home/manuel/Documents/vscode-workspace/product-warehouse-manager-aos
```

###### macOS
Deberemos, primero, compartir con Docker la ruta deseada, tal y como se muestra en la imagen:

![macOS file sharing](/docs/img/volume-macos.png)

Después, será suficiente con establecer el path en el que se encuentre el proyecto:

```yaml
hostPath:
    path: /Users/manuel/Documents/vscode-workspace/product-warehouse-manager-aos
```

###### Windows con Hyper-V
Primero, al igual que en **macOS**, deberemos compartir la ruta deseada:

![Windows Hyper-V file sharing](/docs/img/volume-windows.png)

La diferencia respecto con **macOS** es que no hay ruta directa, y deberemos escribir la ruta precedida de `/host_mnt` y la letra del disco en minúscula:

```yaml
hostPath:
    path: /host_mnt/c/Users/manuel/Documents/vscode-workspace/product-warehouse-manager-aos
```

###### Windows con WSL2
Si utilizamos el subsistema de Linux como backend, no hace falta compartir ninguna ruta, pues ya está montada por defecto, sin embargo, la ruta para acceder cambia incluso que con el backend de Hyper-V, precedido de `/run/desktop/mnt/host`:

```yaml
hostPath:
    path: /run/desktop/mnt/host/c/Users/manuel/Documents/vscode-workspace/product-warehouse-manager-aos
```

###### Despliegue
Para su despliegue, ejecutaremos el siguiente comando:

```console
kubectl apply -f k8s-volume.yaml
```

Una vez acabemos, ejecutaremos el siguiente comando:

```console
kubectl delete -f k8s-volume.yaml
```

##### Opción 2: uso de imágenes construidas
Para este caso omitiremos el uso de volúmenes, pero igualmente tendremos que construir las imágenes con los ficheros que necesitamos para crear y ejecutar los contenedores.

Ejecutaremos los siguientes comandos en el **directorio raíz** de este proyecto en una consola con los privilegios necesarios para construir cada una de las imágenes a usar:

```console
docker build -t product-warehouse-manager-aos/invoicing-api:latest -f .docker/invoicing-api/Dockerfile .
docker build -t product-warehouse-manager-aos/orders-api:latest -f .docker/orders-api/Dockerfile .
docker build -t product-warehouse-manager-aos/products-api:latest -f .docker/products-api/Dockerfile .
docker build -t product-warehouse-manager-aos/swagger-ui:latest -f .docker/swagger-ui/Dockerfile .
```

Una vez construídos, será tan sencillo como ejecutar el siguiente comando para realizar el despliegue:

```console
kubectl apply -f k8s-built.yaml
```

Una vez acabemos, ejecutaremos el siguiente comando:

```console
kubectl delete -f k8s-built.yaml
```

También podremos eliminar las imágenes creadas con:

```console
docker rmi product-warehouse-manager-aos/invoicing-api:latest product-warehouse-manager-aos/orders-api:latest product-warehouse-manager-aos/products-api:latest product-warehouse-manager-aos/swagger-ui:latest
```
