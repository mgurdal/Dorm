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

# Actions

```python
from models import City
```
## create a node instance
```python
d.create_node()
```

## create a table in node
```python
d.add(City) 
```

## create a model instance
```python
c = City(id=123, city="Isparta", location=(12.123, 13.123)) 
```

## save
```python
d.save(c) 
```

## find all cities in the system (lazy)
```python
cities = d.find('City').select().all()
```

## start fetching
```python
city_list = list(cities)
```
