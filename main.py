from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import Response
from bson import ObjectId
from pydantic import BaseModel
from typing import List, Optional
import uuid

from fastapi.openapi.utils import get_openapi
import yaml

from fastapi_versioning import VersionedFastAPI, version

from fastapi.security import HTTPBasic, HTTPBasicCredentials

from auth import authenticate

# Sección mongo: importar librería
import pymongo

import spotipy

sp = spotipy.Spotify(auth_manager=spotipy.oauth2.SpotifyClientCredentials(
    client_id='c8519595485648c3949369793de3e366',
    client_secret='d266e54ea24346a7b278445be87cd400'
))

description = """
Utpl Interoperabilidad API ayuda a describir las capacidades de un directorio. 🚀

## Empresas

Tu puedes crear una empresa.
Tu puedes listar empresas.


## Personas

You will be able to:

* **Crear persona** (_not implemented_).
"""

tags_metadata = [
    {
        "name": "empresas",
        "description": "Permite realizar un CRUD completo de una empresa (listar)"
    },
    {
        "name": "personas",
        "description": "Permite realizar un CRUD completo de una persona"
    },
]

app = FastAPI(
    title="Utpl Interoperabilidad APP",
    description=description,
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Diego Sarmiento",
        "url": "http://x-force.example.com/contact/",
        "email": "dfsarmiento@utpl.edu.ec",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    openapi_tags=tags_metadata
)

# Variables para el usuario y contraseña de administrador
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# Para agregar seguridad a nuestro API
security = HTTPBasic()

# Verificación de las credenciales de autenticación
def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != ADMIN_USERNAME or credentials.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    return credentials

# Configuración de MongoDB
cliente = pymongo.MongoClient("mongodb+srv://utplinteroperabilidad:0b1Fd3PFZZInSuZK@cluster0.susnphb.mongodb.net/?retryWrites=true&w=majority")
database = cliente["empresas"]
coleccion_empresas = database["empresa"]
coleccion_personas = database["persona"]

# Generar la definicion Swagger/OpenAPI
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Utpl Interoperabilidad APP",
        version="0.0.1",
        description=description,
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Ruta para obtener la definicion Swagger en formato YAML
@app.get("/swagger.yaml")
async def get_swagger_yaml():
    response = app.openapi()
    yaml_data = yaml.dump(response)
    return Response(content=yaml_data, media_type="text/vnd.yaml")

# Ruta para la documentación interactiva de Swagger
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    response = get_swagger_ui_html(openapi_url="/swagger.yaml", title="Interoperabilidad API")
    return response

# Ruta de redireccionamiento para la documentación interactiva de Swagger
@app.get("/docs/", include_in_schema=False)
async def redirect_to_custom_swagger_ui():
    return RedirectResponse("/docs")

# Ruta para el favicon de Swagger UI (opcional)
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return ""

# Ruta para la página de inicio de la documentación interactiva de Swagger
@app.get("/", include_in_schema=False)
async def redirect_to_swagger_ui():
    return RedirectResponse("/docs")

class EmpresaRepositorio(BaseModel):
    id: str
    nombre: str
    pais: str
    identificacion: Optional[str] = None
    ciudad: Optional[str] = None
    telefono: Optional[str] = None

class EmpresaEntrada(BaseModel):
    nombre: str
    pais: str
    ciudad: Optional[str] = None

class EmpresaEntradaV2(BaseModel):
    nombre: str
    pais: str
    identificacion: str
    ciudad: Optional[str] = None

class EmpresaEntradaV3(BaseModel):
    nombre: str
    pais: str
    identificacion: str
    ciudad: Optional[str] = None
    telefono: Optional[str] = None

class PersonaRepositorio(BaseModel):
    id: str
    nombre: str
    apellido: str
    edad: int
    email: str
    telefono: str
    direccion: str

class PersonaEntrada(BaseModel):
    nombre: str
    apellido: str
    edad: int
    email: str

class PersonaEntradaV2(BaseModel):
    nombre: str
    apellido: str
    edad: int
    email: str
    telefono: Optional[str] = None

class PersonaEntradaV3(BaseModel):
    nombre: str
    apellido: str
    edad: int
    email: str
    telefono: str
    direccion: str

@app.post("/empresas", response_model=EmpresaRepositorio, tags=["empresas"])
@version(1, 0)
async def crear_empresa(empE: EmpresaEntrada):
    itemEmpresa = EmpresaRepositorio(id=str(uuid.uuid4()), nombre=empE.nombre, pais=empE.pais, ciudad=empE.ciudad)
    resultadoDB = coleccion_empresas.insert_one(itemEmpresa.dict())
    return itemEmpresa

@app.post("/empresas", response_model=EmpresaRepositorio, tags=["empresas"])
@version(2, 0)
async def crear_empresav2(empE: EmpresaEntradaV2):
    itemEmpresa = EmpresaRepositorio(id=str(uuid.uuid4()), nombre=empE.nombre, pais=empE.pais, ciudad=empE.ciudad, identificacion=empE.identificacion)
    resultadoDB = coleccion_empresas.insert_one(itemEmpresa.dict())
    return itemEmpresa

@app.post("/empresas", response_model=EmpresaRepositorio, tags=["empresas"])
@version(3, 0)
async def crear_empresav3(empE: EmpresaEntradaV3):
    itemEmpresa = EmpresaRepositorio(id=str(uuid.uuid4()), nombre=empE.nombre, pais=empE.pais, ciudad=empE.ciudad, identificacion=empE.identificacion, telefono=empE.telefono)
    resultadoDB = coleccion_empresas.insert_one(itemEmpresa.dict())
    return itemEmpresa

@app.get("/empresas", response_model=List[EmpresaRepositorio], tags=["empresas"])
@version(1, 0)
def get_empresas(credentials: HTTPBasicCredentials = Depends(verify_credentials)):
    authenticate(credentials)
    items = list(coleccion_empresas.find())
    return items

@app.get("/empresas", response_model=List[EmpresaRepositorio], tags=["empresas"])
@version(2, 0)
def get_empresasv2(credentials: HTTPBasicCredentials = Depends(verify_credentials)):
    authenticate(credentials)
    items = list(coleccion_empresas.find())
    return items

@app.get("/empresas", response_model=List[EmpresaRepositorio], tags=["empresas"])
@version(3, 0)
def get_empresasv3(credentials: HTTPBasicCredentials = Depends(verify_credentials)):
    authenticate(credentials)
    items = list(coleccion_empresas.find())
    return items

@app.get("/empresas/{empresa_id}", response_model=EmpresaRepositorio, tags=["empresas"])
@version(1, 0)
async def obtener_empresa(empresa_id: str):
    empresa = coleccion_empresas.find_one({"id": empresa_id})
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    return empresa

@app.get("/empresas/{empresa_id}", response_model=EmpresaRepositorio, tags=["empresas"])
@version(2, 0)
async def obtener_empresa(empresa_id: str):
    empresa = coleccion_empresas.find_one({"id": empresa_id})
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    return empresa

@app.get("/empresas/{empresa_id}", response_model=EmpresaRepositorio, tags=["empresas"])
@version(3, 0)
async def obtener_empresa(empresa_id: str):
    empresa = coleccion_empresas.find_one({"id": empresa_id})
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    return empresa

@app.delete("/empresas/{empresa_id}", response_model=EmpresaRepositorio, tags=["empresas"])
@version(1, 0)
async def eliminar_empresa(empresa_id: str):
    empresa = coleccion_empresas.find_one({"id": empresa_id})
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    coleccion_empresas.delete_one({"id": empresa_id})
    return empresa

@app.delete("/empresas/{empresa_id}", response_model=EmpresaRepositorio, tags=["empresas"])
@version(2, 0)
async def eliminar_empresa(empresa_id: str):
    empresa = coleccion_empresas.find_one({"id": empresa_id})
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    coleccion_empresas.delete_one({"id": empresa_id})
    return empresa

@app.delete("/empresas/{empresa_id}", response_model=EmpresaRepositorio, tags=["empresas"])
@version(3, 0)
async def eliminar_empresa(empresa_id: str):
    empresa = coleccion_empresas.find_one({"id": empresa_id})
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    coleccion_empresas.delete_one({"id": empresa_id})
    return empresa

@app.post("/personas", response_model=PersonaRepositorio, tags=["personas"])
@version(1, 0)
async def crear_persona(persona: PersonaEntrada):
    itemPersona = PersonaRepositorio(
        id=str(uuid.uuid4()),
        nombre=persona.nombre,
        apellido=persona.apellido,
        edad=persona.edad,
        email=persona.email,
        telefono="", # Siendo v1, no necesitamos el campo "telefono"
        direccion="" # Ni el campo "direccion"
    )
    resultadoDB = coleccion_personas.insert_one(itemPersona.dict())
    return itemPersona

@app.post("/personas", response_model=PersonaRepositorio, tags=["personas"])
@version(2, 0)
async def crear_persona_v2(persona: PersonaEntradaV2):
    itemPersona = PersonaRepositorio(
        id=str(uuid.uuid4()),
        nombre=persona.nombre,
        apellido=persona.apellido,
        edad=persona.edad,
        email=persona.email,
        telefono=persona.telefono, # Siendo v2, agregamos el campo "telefono"
        direccion="" # Pero no necesitamos el campo "direccion"
    )
    resultadoDB = coleccion_personas.insert_one(itemPersona.dict())
    return itemPersona

@app.post("/personas", response_model=PersonaRepositorio, tags=["personas"])
@version(3, 0)
async def crear_persona_v3(persona: PersonaEntradaV3):
    itemPersona = PersonaRepositorio(
        id=str(uuid.uuid4()),
        nombre=persona.nombre,
        apellido=persona.apellido,
        edad=persona.edad,
        email=persona.email,
        telefono=persona.telefono, # Siendo v3, agregamos el campo "telefono"
        direccion=persona.direccion # Y también el campo "direccion"
    )
    resultadoDB = coleccion_personas.insert_one(itemPersona.dict())
    return itemPersona

@app.get("/personas", response_model=List[PersonaRepositorio], tags=["personas"])
@version(1, 0)
def get_personas(credentials: HTTPBasicCredentials = Depends(verify_credentials)):
    authenticate(credentials)
    items = list(coleccion_personas.find())
    return items

@app.get("/personas", response_model=List[PersonaRepositorio], tags=["personas"])
@version(2, 0)
def get_personas_v2(credentials: HTTPBasicCredentials = Depends(verify_credentials)):
    authenticate(credentials)
    items = list(coleccion_personas.find())
    return items

@app.get("/personas", response_model=List[PersonaRepositorio], tags=["personas"])
@version(3, 0)
def get_personas_v3(credentials: HTTPBasicCredentials = Depends(verify_credentials)):
    authenticate(credentials)
    items = list(coleccion_personas.find())
    return items

@app.get("/personas/{persona_id}", tags=["personas"])
@version(1, 0)
async def obtener_persona(persona_id: str):
    persona = coleccion_personas.find_one({"id": persona_id})
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    return PersonaRepositorio(**persona)

@app.get("/personas/{persona_id}", tags=["personas"])
@version(2, 0)
async def obtener_personav2(persona_id: str):
    persona = coleccion_personas.find_one({"id": persona_id})
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    return PersonaRepositorio(**persona)

@app.get("/personas/{persona_id}", tags=["personas"])
@version(3, 0)
async def obtener_personav3(persona_id: str):
    persona = coleccion_personas.find_one({"id": persona_id})
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    return PersonaRepositorio(**persona)

@app.delete("/personas/{persona_id}", response_model=PersonaRepositorio, tags=["personas"])
@version(1, 0)
async def eliminar_persona(persona_id: str):
    persona = coleccion_personas.find_one({"id": persona_id})
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    coleccion_personas.delete_one({"id": persona_id})
    return PersonaRepositorio(**persona)

@app.delete("/personas/{persona_id}", response_model=PersonaRepositorio, tags=["personas"])
@version(2, 0)
async def eliminar_persona_v2(persona_id: str):
    persona = coleccion_personas.find_one({"id": persona_id})
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    coleccion_personas.delete_one({"id": persona_id})
    return PersonaRepositorio(**persona)

@app.delete("/personas/{persona_id}", response_model=PersonaRepositorio, tags=["personas"])
@version(3, 0)
async def eliminar_persona_v3(persona_id: str):
    persona = coleccion_personas.find_one({"id": persona_id})
    if not persona:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    coleccion_personas.delete_one({"id": persona_id})
    return PersonaRepositorio(**persona)

@app.get("/")
def read_root():
    return {"Hello": "Interoperabilidad"}

app = VersionedFastAPI(app)
