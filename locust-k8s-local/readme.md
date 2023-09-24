# Requarment
### As we are deploying the locust in k8s cluster in local server so we need to deploy a k8s cluster
# Step-1: Deploy k8s
### To deploy k8s cluster in local server please follow https://github.com/naimul3070/kubernetes.git

# Step-2: Setup nfs Server


### Install nfs server
    sudo apt update
    sudo apt install nfs-kernel-server
### change ownership

     sudo chown nobody:nogroup /home/devops DevOps-Deployment/locust-k8s-local/locast_data

### Configuring the NFS Exports 
    sudo vim /etc/exports  (insert the below line in this file)
###
    /home/devops/kubernetes-locust-example/locast_data  172.25.80.0/22(rw,sync,no_subtree_check)
### To export the directory and make it available,
    sudo exportfs -a
### nfs service restart
    sudo systemctl status nfs-server


# Step-3: Deploy Locust

### Clone the repository
    git clone https://github.com/Technoaidbd24/DevOps-Deployment.git
###

    cd /home/devops/DevOps-Deployment/locust-k8s-local/k8s
### open persistence volume yaml file and define the nfs server ip in `server` portion

    vim pv-locust.yaml
###
    apiVersion: v1

    kind: PersistentVolume

    metadata:

      name: pv-vol1

    spec:

      storageClassName: nfs
      
      accessModes: [ "ReadWriteOnce" ]
      
      capacity:
      
      storage: 1Gi
      
      nfs:
      
      server: <nfs-server-ip>
    
      path: /home/devops/kubernetes-locust-example/locast_data
      
    :x 

### deploy the service,deployment,volume 
    kubectl apply -f locust-master-deployment.yaml -f locust-master-service.yaml -f locust-worker-deployment.yaml -f pvc-locust.yaml -f pv-locust.yaml

# Step-4:  

### To browse the locust follow the below link

    http://<server-ip>:30627
  

