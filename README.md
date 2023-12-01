# orchestration-at-scale-23-24-polymetrie-d

### Accessing Kubernetes Dashboard
Run ```kube proxy``` <br>
Run ``kubectl -n kubernetes-dashboard create token admin-user`` to generate new login token <br> 
Go here http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/#/workloads?namespace=default <br>
