# Kubernetes
## Скачивание и развертывание
```
sudo apt update
sudo apt upgrade
sudo apt install software-properties-common apt-transport-https ca-certificates gnupg2 gpg sudo
swapoff -a
sudo modprobe overlay
sudo modprobe br_netfilter
echo "overlay" | sudo tee -a /etc/modules
echo "br_netfilter" | sudo tee -a /etc/modules
echo 1 | sudo tee /proc/sys/net/ipv4/ip_forward
sudo mkdir /etc/apt/keyrings
sudo curl -fsSLo /etc/apt/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg
echo "deb [signed-by=/etc/apt/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list

sudo apt-get update
# apt-transport-https may be a dummy package; if so, you can skip that package
sudo apt-get install -y apt-transport-https ca-certificates curl gpg
# If the directory `/etc/apt/keyrings` does not exist, it should be created before the curl command, read the note below.
# sudo mkdir -p -m 755 /etc/apt/keyrings
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.33/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
# This overwrites any existing configuration in /etc/apt/sources.list.d/kubernetes.list
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.33/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update
sudo apt-get install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl

export OS=xUbuntu_22.04
export VERSION=1.24
echo "deb https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/$OS/ /" | sudo tee /etc/apt/sources.list.d/devel:kubic:libcontainers:stable.list
echo "deb http://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable:/cri-o:/$VERSION/$OS/ /" | sudo tee /etc/apt/sources.list.d/devel:kubic:libcontainers:stable:cri-o:$VERSION.list
curl -L https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable:/cri-o:/$VERSION/$OS/Release.key | sudo apt-key add -
curl -L https://download.opensuse.org/repositories/devel:/kubic:/libcontainers:/stable/$OS/Release.key | sudo apt-key add -
sudo apt-get update
sudo apt-get install -y cri-o cri-o-runc
sudo systemctl enable crio
sudo systemctl start crio
sudo kubeadm init --pod-network-cidr=10.100.0.0/16
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

sudo apt update
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io
sudo systemctl enable docker

kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml
kubectl get pods -n kube-system

cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-front-to-backend
spec:
  podSelector:
    matchLabels:
      app: runtime
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: front
    ports:
    - protocol: TCP
      port: 8001
EOF

export BACKEND_IP=$(kubectl get service runtime-service -o jsonpath='{.spec.clusterIP}')

# Обновление фронтенда с явным IP
kubectl patch deployment front-deployment -p "{\"spec\":{\"template\":{\"spec\":{\"containers\":[{\"name\":\"front\",\"env\":[{\"name\":\"BACKEND_URL\",\"value\":\"http://$BACKEND_IP:8001\"}]}]}}}}"

kubectl rollout restart deployment front-deployment
kubectl rollout restart deployment runtime-deployment

cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: coredns
  namespace: kube-system
data:
  Corefile: |
    .:53 {
        errors
        health
        ready
        forward . 8.8.8.8 8.8.4.4
        cache 30
        loop
        reload
        loadbalance
    }
EOF
kubectl rollout restart deployment -n kube-system coredns
```

 Нужно также установить yc и авторизоваться в регистри.

Для сброса `sudo kubeadm reset`
Для запуска воркера: `sudo kubeadm join {IP} --token {TOKEN} --discovery-token-ca-cert-hash {HASH} --cri-socket unix:///var/run/crio/crio.sock`

`sudo kubectl --kubeconfig=/etc/kubernetes/admin.conf get nodes`


## Нагрузка на CPU и автомасштабирование
```
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
kubectl patch deployment runtime-deployment -p '{
  "spec": {
    "template": {
      "spec": {
        "containers": [{
          "name": "runtime",
          "resources": {
            "requests": {
              "cpu": "100m",
              "memory": "128Mi"
            },
            "limits": {
              "cpu": "500m",
              "memory": "512Mi"
            }
          }
        }]
      }
    }
  }
}'

cat <<EOF | kubectl apply -f -
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: runtime-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: runtime-deployment
  minReplicas: 1
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 15
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 30
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
    scaleDown:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 50
        periodSeconds: 30
EOF

kubectl patch deployment metrics-server -n kube-system --type='json' -p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}]'
```

## Метрики и мониторинги
Установка helm:
```
curl https://baltocdn.com/helm/signing.asc | gpg --dearmor | sudo tee /usr/share/keyrings/helm.gpg > /dev/null
sudo apt-get install apt-transport-https --yes
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
sudo apt-get update
sudo apt-get install helm
```

Прометея:
```
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

kubectl create namespace monitoring

cat > prometheus-values.yaml << EOF
server:
  persistentVolume:
    enabled: true
    size: 10Gi
  retention: 15d
  
alertmanager:
  enabled: true
  persistentVolume:
    enabled: true
    size: 2Gi

nodeExporter:
  enabled: true

kubeStateMetrics:
  enabled: true

pushgateway:
  enabled: true

prometheus-node-exporter:
  hostRootFsMount:
    enabled: true
EOF

helm install prometheus prometheus-community/prometheus \
  --namespace monitoring \
  --values prometheus-values.yaml
```

Графаны:
```
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

cat > grafana-values.yaml << EOF
persistence:
  enabled: true
  size: 5Gi

datasources:
  datasources.yaml:
    apiVersion: 1
    datasources:
    - name: Prometheus
      type: prometheus
      url: http://prometheus-server.monitoring.svc.cluster.local
      access: proxy
      isDefault: true

dashboardProviders:
  dashboardproviders.yaml:
    apiVersion: 1
    providers:
    - name: 'default'
      orgId: 1
      folder: ''
      type: file
      disableDeletion: false
      editable: true
      options:
        path: /var/lib/grafana/dashboards/default

dashboards:
  default:
    kubernetes-pod-metrics:
      gnetId: 6417
      revision: 1
      datasource: Prometheus
    kubernetes-cluster:
      gnetId: 7249
      revision: 1
      datasource: Prometheus
    node-exporter:
      gnetId: 1860
      revision: 23
      datasource: Prometheus
    app-metrics:
      gnetId: 10280
      revision: 1
      datasource: Prometheus

service:
  type: LoadBalancer

adminPassword: strongpassword
EOF

helm install grafana grafana/grafana \
  --namespace monitoring \
  --values grafana-values.yaml
```

Настройка:
```
kubectl patch deployment runtime-deployment --type=json -p='[
  {
    "op": "add", 
    "path": "/spec/template/metadata/annotations", 
    "value": {
      "prometheus.io/scrape": "true",
      "prometheus.io/port": "8080",
      "prometheus.io/path": "/metrics"
    }
  }
]'
```

Сервис-монитор:
```
cat > runtime-servicemonitor.yaml << EOF
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: runtime-monitor
  namespace: monitoring
  labels:
    release: prometheus
spec:
  selector:
    matchLabels:
      app: runtime
  endpoints:
  - port: http
    interval: 15s
    path: /metrics
  namespaceSelector:
    matchNames:
    - default
EOF

kubectl apply -f runtime-servicemonitor.yaml
```

Починка:
```
cat > grafana-values-no-pv.yaml << EOF
persistence:
  enabled: false

service:
  type: NodePort
EOF

helm upgrade grafana grafana/grafana \
  --namespace monitoring \
  --values grafana-values-no-pv.yaml

cat > prometheus-values-no-pv.yaml << EOF
server:
  persistentVolume:
    enabled: false

alertmanager:
  persistentVolume:
    enabled: false
EOF

helm upgrade prometheus prometheus-community/prometheus \
  --namespace monitoring \
  --values prometheus-values-no-pv.yaml
```

