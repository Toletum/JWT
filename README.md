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

## Architecture and task plan

- Architecture: FastAPI application in `app.py`, with in-memory user records and JWT authentication.
- [x] Add a string `session_secret` field to each `USUARIOS_DB` user record.
- [x] Generate each user's value with `secrets.token_hex(16)`.
- [x] Use each user's `session_secret` when signing and validating tokens, including expiration checks.
- [x] Validate the token/session-secret behavior with the available checks.

## Launch plan

- Architecture: FastAPI app served by Uvicorn; project rules require running web servers through rootless Podman.
- [x] Check for existing Podman image/build and run configuration.
- [x] Launch the app through rootless Podman and report its local URL.

## Test plan

- Architecture: tests under `tests/` cover JWT helper functions and HTTP endpoints; endpoint checks use `curl` against the local app.
- [x] Create a `tests/` directory and add tests for valid, expired, wrong-secret, missing-expiration, and unknown-user tokens.
- [x] Run the unit tests with the project virtual environment.
- [x] Add curl-based checks for health, valid login/profile access, invalid login, and missing/invalid bearer tokens.
- [x] Run the API checks against the server on localhost:8000.
- Test command: `./.venv/bin/python -m unittest discover -s tests -v` (keep the app running on localhost:8000 for the curl tests).

## Pull request plan

- Architecture: create a PR from this repository's current branch and configured Git remote.
- [x] Inspect the working-tree changes and remote hosting setup to determine the PR scope and target.
- [x] Commit and push only the intended changes, then open the PR if the hosting CLI and credentials are available.
