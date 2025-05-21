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
