# orchestration-at-scale-23-24-polymetrie-d

### Accessing Kubernetes Dashboard
Run ```kubectl proxy``` <br> <br>
Run ``kubectl -n kubernetes-dashboard create token admin-user`` to generate new login token <br> <br>
Go here http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/#/workloads?namespace=default <br> <br>

### Accesssing Deployment
Run ``kubectl port-forward POD_NAME MACHINE_PORT:EXPOSED_POD_PORT`` <br> 
Or <br> 
Use LoadBalancer's public IP from ``kubectl get svc``
