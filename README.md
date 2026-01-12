# Floodcast
Flood prediction service.

## Project organisation
If you want to share some notes, links, or documentation, check the [wiki](https://github.com/insa-resq/floodcast/wiki).

## Running

The recommended way to get everything running is using docker compose. This will start each service in it's own container.

Development (with hot reload, open on localhost:8000, individual services open on localhost:800n)
```bash
sudo docker compose up
```

Production
```bash
sudo docker compose -f compose.prod.yml up
```

## Eco-design

You should have jupyter installed to re-run the code.

The code logic is in modelisation.ipynb

**Source code for efootprint module** : https://github.com/Boavizta/e-footprint
**Documentation** : https://boavizta.github.io/e-footprint/

```bash
python -m venv .venv 

pip install efootprint

jupyter notebook

```