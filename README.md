# JWT

Ejemplo de autenticación con JWT usando FastAPI y PyJWT.

## Requisitos

- Python 3.10+

## Instalación

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Ejecución

```bash
uvicorn app:app --reload
```

Documentación interactiva: http://127.0.0.1:8000/docs

## Endpoints

| Método | Ruta         | Descripción                                    |
| ------ | ------------ | ---------------------------------------------- |
| GET    | `/health`    | Verifica que el servidor está activo (público) |
| POST   | `/token`     | Autentica usuario y devuelve el token JWT      |
| GET    | `/users/me`  | Devuelve el usuario actual (requiere token)    |

## Uso

```bash
# Obtener token
curl -X POST http://127.0.0.1:8000/token \
  -d "username=juan&password=password123"

# Consultar usuario autenticado
curl http://127.0.0.1:8000/users/me \
  -H "Authorization: Bearer <access_token>"
```

## Usuarios de prueba

| Usuario | Contraseña    |
| ------- | ------------- |
| juan    | password123   |
| maria   | secreto456    |

## Nota

La `SECRET_KEY` y los usuarios están definidos en memoria en `app.py` con fines
demostrativos. En producción deben venir de variables de entorno y una base de
datos real.
