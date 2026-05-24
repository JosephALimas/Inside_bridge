# Manual de instalacion

## 1. Preparar el entorno

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Configurar variables

```bash
copy .env.example .env
```

Edita `.env` y cambia `SECRET_KEY` para ambientes compartidos o produccion.

## 3. Crear la base de datos

```bash
flask --app run.py init-db
```

Esto crea las tablas y registra los roles base: `admin` y `member`.

## 4. Ejecutar la aplicacion

```bash
flask --app run.py run --debug
```

Abre `http://127.0.0.1:5000`.

## 5. Crear un administrador

```bash
flask --app run.py create-admin
```

## 6. Ejecutar pruebas

```bash
pytest
```

## 7. Ejecutar con Docker

```bash
docker compose up --build
```

La aplicacion quedara disponible en `http://localhost:5000`.
