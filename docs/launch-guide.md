# Launch guide
In this section, you can find all the different ways to launch Prism

- <a href="#production">Production</a>
- <a href="#development">Development</a>
- <a href="#tests">Tests</a>

## Production
### Launch containers
```
docker compose --profile prod up --build -d
```
### Stop containers
```
docker compose --profile prod down
```
`-v` - use this flag if you want to delete the database
### View logs
```
docker compose --profile prod logs > logs.txt
```
### Restart
```
docker compose --profile prod restart
```


## Development
### Launch containers
```
docker compose --profile test up --build -d
```
### Stop containers
```
docker compose --profile test down
```
`-v` - use this flag if you want to delete the database
### View logs
```
docker compose --profile test logs > logs.txt
```
### Restart
```
docker compose --profile test restart
```


## Tests
```
docker compose --profile test up -d
docker exec -it testprism pytest -v
docker compose --profile test down -v
```

