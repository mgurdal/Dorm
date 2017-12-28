# Norm

## create network
```
docker network create dorm_net
```

## create postgres instance
```
sudo docker run --network dorm_net dorm_postgres
```

## select q
```
from models import *
 d.collect_models()
 list(d.find('city').select().all())
```
