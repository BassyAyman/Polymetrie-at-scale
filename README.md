# orchestration-at-scale-23-24-polymetrie-d

### Accessing Kubernetes Dashboard
Run ```kubectl proxy```. <br> <br>
Run ``kubectl -n kubernetes-dashboard create token admin-user`` to generate new login token. <br> <br>
Go here http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/#/workloads?namespace=default <br> <br>

### Accesssing Deployment
Run ``kubectl port-forward POD_NAME MACHINE_PORT:EXPOSED_POD_PORT`` <br> 
Or <br> 
Use LoadBalancer's public IP from ``kubectl get svc``.

### Postgresql and Redis deployment 
Add bitnami repo ``helm repo add bitnami https://charts.bitnami.com/bitnami``. <br>
Run ``helm install -f postgres_values.yml my-postgresql bitnami/postgresql`` for posgresql database. <br>
Run ``helm install my-redis bitnami/redis`` for redis. <br> <br>
For more information about how to connect to these resources run ``helm status my-postgresql`` or ``helm status my-redis``.
