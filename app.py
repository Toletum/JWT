from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

app = FastAPI(title="Ejemplo FastAPI + JWT Optimizado")

# --- CONFIGURACIÓN DE SEGURIDAD ---
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- "BASE DE DATOS" EN MEMORIA ---
USUARIOS_DB = {
    "juan": {
        "username": "juan",
        "email": "juan@example.com",
        "password": "password123",
        "disabled": False,
        "session_secret": '39e082580e07e09ed65657c1be4062e6'
    },
    "maria": {
        "username": "maria",
        "email": "maria@example.com",
        "password": "secreto456",
        "disabled": False,
        "session_secret": 'fd753ad1dc0d3263b45abdca142a43b1'
    }
}

# --- MODELOS PYDANTIC ---
class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    username: str
    email: str | None = None
    disabled: bool | None = None

class HealthResponse(BaseModel):
    status: str
    timestamp: str

# --- FUNCIONES AUXILIARES ---
def autenticar_usuario(username: str, password: str):
    usuario = USUARIOS_DB.get(username)
    if not usuario:
        return False
    if usuario["password"] != password:
        return False
    return usuario

def crear_token_acceso(
    data: dict, session_secret: str, expires_delta: timedelta | None = None
):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, session_secret, algorithm=ALGORITHM)
    return encoded_jwt

def obtener_usuario_actual(token: Annotated[str, Depends(oauth2_scheme)]):
    credenciales_excepcion = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        unverified_payload = jwt.decode(token, options={"verify_signature": False})
        username: str | None = unverified_payload.get("sub")

        if not username or not isinstance(username, str):
            raise credenciales_excepcion

        usuario = USUARIOS_DB.get(username)
        if usuario is None:
            raise credenciales_excepcion

        jwt.decode(
            token,
            usuario["session_secret"],
            algorithms=[ALGORITHM],
            options={"require": ["exp", "sub"]},
        )
    except jwt.PyJWTError:
        raise credenciales_excepcion

    return usuario

# --- ENDPOINTS ---

@app.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check():
    """Endpoint público para verificar que el servidor está activo."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.post("/token", response_model=Token)
async def login_para_obtener_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    usuario = autenticar_usuario(form_data.username, form_data.password)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = crear_token_acceso(
        data={"sub": usuario["username"]},
        session_secret=usuario["session_secret"],
        expires_delta=access_token_expires,
    )

    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=UserResponse)
async def leer_usuario_actual(
    current_user: Annotated[dict, Depends(obtener_usuario_actual)]
):
    return current_user
