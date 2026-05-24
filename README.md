# Inside Bridge

Inside Bridge es una aplicacion web server-side rendered con Flask que conecta turistas y personas nuevas en Ciudad de Mexico con experiencias locales, eventos y negocios autenticos. El MVP funciona como un directorio curado: los negocios publican experiencias, un administrador las aprueba y los visitantes las descubren en un catalogo publico.

## Requisitos

- Python 3.11+
- pip
- Docker y Docker Compose, opcional para contenedores

## Instalacion local

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
flask --app run.py init-db
flask --app run.py run --debug
```

La aplicacion queda disponible en `http://127.0.0.1:5000`.

## Comandos utiles

```bash
pytest
flask --app run.py init-db
flask --app run.py create-admin
```

## Flujo MVP

1. Un administrador inicializa la base de datos y crea una cuenta admin.
2. Un negocio se registra como `business`.
3. El negocio completa su perfil comercial.
4. El negocio crea una experiencia con contenido en espanol e ingles.
5. El admin aprueba o rechaza la experiencia.
6. Los visitantes consultan `/experiences` y contactan al negocio por WhatsApp o email.

## Docker

```bash
docker compose up --build
```

La app se expone en `http://localhost:5000`.

## Estructura

```text
app/
  admin/           Moderacion de experiencias
  auth/            Rutas de login, registro y logout
  business/        Panel de negocios locales
  experiences/     Catalogo publico
  main/            Paginas principales y dashboard
  templates/       Vistas Jinja2
  static/          CSS e imagenes
  config.py        Configuracion central
  extensions.py    Extensiones Flask
  models.py        Modelos SQLAlchemy
tests/             Pruebas con pytest
docs/              Manual de instalacion
```
