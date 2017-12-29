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
# coding: utf-8
from models import City
d.create_node()
c = City(id=123, city="Isparta", location=(12.123, 13.123))
d.add(City)
d.save(c)
d.collect_models()
d.find('City').select().all().__next__()

```
