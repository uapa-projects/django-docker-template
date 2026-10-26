# django-docker-template

Plantilla base para proyectos Django que en producción corren en Docker
(Gunicorn + Nginx) bajo un prefijo del dominio, por ejemplo `https://dominio/app1/`.

## Crear un proyecto nuevo

1. En GitHub: **Use this template** → **Create a new repository**.
2. Clonar el repo nuevo y preparar el entorno local:
   ```bash
   python3 -m venv venv
   venv/bin/pip install -r requirements.txt
   cp .env.example .env          # DEBUG=True, el resto vacío
   venv/bin/python manage.py migrate
   venv/bin/python manage.py runserver
   ```

En local se usa SQLite (`db.sqlite3`) y no hace falta Docker.

## Estructura

| Archivo | Para qué |
|---|---|
| `core/` | Paquete del proyecto Django (settings, urls, wsgi) |
| `requirements.txt` | Dependencias de la app (local y producción) |
| `requirements-prod.txt` | Lo anterior + Gunicorn y el driver de Postgres |
| `Dockerfile` | Imagen de la app; arranca con `entrypoint.sh` |
| `entrypoint.sh` | En cada arranque: `migrate`, `collectstatic` y luego Gunicorn |
| `docker-compose.yml` | Servicios `web` (Gunicorn) y `nginx` |
| `deploy/nginx.conf` | Nginx: sirve `/static/` y pasa el resto a Gunicorn |
| `.env.example` | Variables de configuración documentadas |

## Despliegue en el servidor

```
Apache (dominio/app1/) ──► 127.0.0.1:APP_PORT ──► nginx ──► gunicorn (web:8000)
```

### 1. Primera vez

```bash
git clone <repo> && cd <repo>
cp .env.example .env && chmod 600 .env
nano .env
docker compose up -d --build
docker compose exec web python manage.py createsuperuser
```

`.env` de producción:
```
DEBUG=False
SECRET_KEY=<clave propia>
ALLOWED_HOSTS=dominio.edu.do
APP_PATH=/app1
APP_PORT=8015
DATABASE_URL=postgres://USUARIO:PASSWORD@host.docker.internal:5432/NOMBRE_DB
```

`APP_PATH` y `APP_PORT` deben ser **distintos en cada proyecto** del servidor.

### 2. Apache

Dentro del `<VirtualHost *:443>` del dominio (cambiar `/app1` y `8015` por los del `.env`):

```apache
ProxyPassMatch ^/app1$ !
RedirectMatch 301 ^/app1$ /app1/

ProxyPreserveHost On
RequestHeader set X-Forwarded-Proto "https"
ProxyPass /app1/ http://127.0.0.1:8015/
ProxyPassReverse /app1/ http://127.0.0.1:8015/
```

El destino va **sin** el prefijo: Apache lo quita y Django lo vuelve a poner en las URLs
(`FORCE_SCRIPT_NAME` a partir de `APP_PATH`).

```bash
sudo a2enmod proxy proxy_http headers
sudo apachectl configtest && sudo systemctl reload apache2
```

### 3. Postgres del servidor (fuera de Docker)

El contenedor llega al servidor como `host.docker.internal` (`extra_hosts` en el compose).
Postgres tiene que escuchar en la IP del puente de Docker (`ip -4 addr show docker0`, normalmente `172.17.0.1`):

- `postgresql.conf`: `listen_addresses = 'localhost,172.17.0.1'`
- `pg_hba.conf`: `host  NOMBRE_DB  USUARIO  172.16.0.0/12  scram-sha-256`
- `sudo systemctl restart postgresql` (y si hay ufw: `sudo ufw allow from 172.16.0.0/12 to any port 5432`)

Para usar SQLite en producción: `DATABASE_URL=sqlite:////app/data/db.sqlite3` (queda en el volumen `db_volume`).

### Actualizar

```bash
git pull
docker compose up -d --build
```

Si solo cambia el `.env`: `docker compose up -d` (no `restart`, que conserva las variables viejas).

> `docker compose down -v` borra los volúmenes (estáticos y la base SQLite). Para parar sin perder datos: `docker compose down`.
