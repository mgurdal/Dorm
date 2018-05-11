# Norm

## create network
```
docker network create dorm_net
```

## create postgres instance
```
sudo docker run --network dorm_net dorm_postgres
```

## create dorm master instance
```
docker run -it -v /var/run/docker.sock:/var/run/docker.sock dorm_master bash
```


## select q
```
# coding: utf-8
from models import City
d.create_node() # create a node instance
d.add(City) # create a table in node
c = City(id=123, city="Isparta", location=(12.123, 13.123)) # create a model instance
d.save(c) # save to db
<!-- d.collect_models() -->
cities = d.find('City').select().all() # find all cities in system (lazy)
city_list = list(cities) # start fetch
```
