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

## 6. Probar el flujo MVP

1. Entra con la cuenta admin y abre `/admin/experiences`.
2. Registra una cuenta nueva como `Negocio local`.
3. Completa el perfil en `/business/profile`.
4. Crea una experiencia en `/business/experiences/new`.
5. Vuelve como admin, aprueba la experiencia y revisa `/experiences`.

## 7. Ejecutar pruebas

```bash
pytest
```

## 8. Ejecutar con Docker

```bash
docker compose up --build
```

La aplicacion quedara disponible en `http://localhost:5000`.
