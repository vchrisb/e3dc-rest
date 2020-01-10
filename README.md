# e3dc-rest
a simple REST API to access a E3DC system

## Required Configuration

```
export E3DC_IP_ADDRESS='192.168.1.99'
export E3DC_USERNAME='use@domain.com'
export E3DC_PASSWORD='Passw0rd'
export E3DC_KEY='secretkey'
export ADMIN_PASSWORD='admin'
```

## Start local

### Prepare
```
python -m venv .venv
source .venv
pip install -r requirements.txt
```

### Start

Dev Webserver:
```
python api.py
```
or use
```
gunicorn --bind 0.0.0.0:8080 wsgi:app --access-logfile -
```

## Start Docker

```
docker build . -t vchrisb/e3dc-rest
docker run --name e3dc-rest -p 8080:8080 -e E3DC_IP_ADDRESS -e E3DC_USERNAME -e E3DC_PASSWORD -e E3DC_KEY -e ADMIN_PASSWORD="admin" vchrisb/e3dc-rest

```

## Use

```
curl http://admin:admin@localhost:8080/api/poll
curl -H "Content-Type: application/json"  -X POST -d '{"powerLimitsUsed": true,"maxChargePower": 1000,"maxDischargePower": 1300,"dischargeStartPower": 65}' http://admin:admin@127.0.0.1:8080/api/power_settings
curl http://admin:admin@localhost:8080/api/power_settings 
```


