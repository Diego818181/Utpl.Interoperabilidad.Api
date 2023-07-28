
from fastapi.security import HTTPBasicCredentials
from fastapi import HTTPException, Depends

def authenticate(credentials: HTTPBasicCredentials):
    username = credentials.username
    password = credentials.password
    # Aquí puedes verificar las credenciales y realizar la autenticación
    # Por ejemplo, verificar si el usuario y la contraseña son válidos en tu sistema
    # Si no son válidos, puedes lanzar una excepción HTTPException con el código de estado 401 (No autorizado)
    if not (username == "admin" and password == "admin123"):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    return username