#!/bin/bash

# Variables
configmap_name="my-test"
yaml_file="./k6-resource.yaml"
wait_time="11s"
script_name="$1"

# Créer le ConfigMap à partir du fichier donné en argument
kubectl create configmap "$configmap_name" --from-file="$script_name"

# Appliquer le déploiement depuis le fichier k6-resource.yaml
kubectl apply -f "$yaml_file"

echo "Script execution... Wait..."

# Attendre pendant un certain temps défini par la variable wait_time
sleep "$wait_time"

# Supprimer le ConfigMap
kubectl delete configmap "$configmap_name"

# Supprimer le déploiement
kubectl delete -f "$yaml_file"

echo "Script '$script_name' execution done."
