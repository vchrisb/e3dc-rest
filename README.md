# e3dc-rest
This is a simple REST API to access a E3DC system

## Getting Started
This script uses a Python library which can be found here: https://github.com/fsantini/python-e3dc
and exposes the values as REST API endpoints.

The API uses exposed environment variables to access the E3DC.

## Configuring the E3DC correctly
- ToDo...

### Local startup

You need to export the variables so the script can read them
```
export E3DC_IP_ADDRESS='192.168.1.99'
export E3DC_USERNAME='use@domain.com'
export E3DC_PASSWORD='Passw0rd'
export E3DC_KEY='secretkey'
export ADMIN_PASSWORD='admin'
```                                                         

Create a self contained environment
```
python3 -m venv .venv
```

then you can go into the new made environment and install the requirements
```
source .venv/bin/activate
pip3 install -r requirements.txt
```

Dev Webserver:
```
cd api
python3 api.py
```
or use
```
cd api
gunicorn --bind 0.0.0.0:8080 wsgi:app --access-logfile -
```

### Container/Kubernetes

#### Build

```
docker build . -t e3dc-rest
```

#### Docker

```
docker run --name e3dc-rest -p 8080:8080 -e E3DC_IP_ADDRESS -e E3DC_USERNAME -e E3DC_PASSWORD -e E3DC_KEY -e ADMIN_PASSWORD="admin" ghcr.io/vchrisb/e3dc-rest:latest
```

#### Kubernetes

Create Secret:
```
kubectl create secret generic e3dc-secret --from-literal=username='user@domain.com' --from-literal=password='password' --from-literal=ip_address='192.168.1.99' --from-literal=key='password' --from-literal=config='{}' --from-literal=admin_password='admin'
```

Deploy with Ingress Controller:
```
kubectl apply -f ingress.yml -f service-ingress.yml -f deplyoment.yml
```
## Calling the API

```
curl http://admin:admin@localhost:8080/api/poll
curl -H "Content-Type: application/json"  -X POST -d '{"powerLimitsUsed": true,"maxChargePower": 1000,"maxDischargePower": 1300,"dischargeStartPower": 65}' http://admin:admin@127.0.0.1:8080/api/power_settings
curl http://admin:admin@localhost:8080/api/power_settings 
```
