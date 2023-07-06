from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import uuid

from fastapi_versioning import VersionedFastAPI, version

from fastapi.security import HTTPBasic, HTTPBasicCredentials

from auth import authenticate

#seccion mongo importar libreria
import pymongo

import spotipy

sp = spotipy.Spotify(auth_manager=spotipy.oauth2.SpotifyClientCredentials(
    client_id='c8519595485648c3949369793de3e366',
    client_secret='d266e54ea24346a7b278445be87cd400'
))

description = """
Utpl tnteroperabilidad API ayuda a describir las capacidades de un directorio. 🚀

## Empresas

Tu puedes crear una empresa.
Tu puedes listar empresas.


## Artistas

You will be able to:

* **Crear artista** (_not implemented_).
"""

tags_metadata = [
    {
        "name":"empresas",
        "description": "Permite realizar un crud completo de una empresa (listar)"
    },
    {
        "name":"artistas",
        "description": "Permite realizar un crud completo de un artista"
    },
]

app = FastAPI(
    title="Utpl Interoperabilidad APP 2",
    description= description,
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
    openapi_tags = tags_metadata
)

#para agregar seguridad a nuestro api
security = HTTPBasic()

#configuracion de mongo
cliente = pymongo.MongoClient("mongodb+srv://utplinteroperabilidad:0b1Fd3PFZZInSuZK@cluster0.susnphb.mongodb.net/?retryWrites=true&w=majority")
database = cliente["directorio"]
coleccion = database["empresa"]

class EmpresaRepositorio (BaseModel):
    id: str
    nombre: str
    pais: str
    identificacion: Optional[str] = None
    ciudad: Optional[str] = None

class EmpresaEntrada (BaseModel):
    nombre:str
    pais:str
    ciudad: Optional[str] = None

class EmpresaEntradaV2 (BaseModel):
    nombre:str
    pais:str
    identificacion:str
    ciudad: Optional[str] = None


empresaList = []

@app.post("/empresas", response_model=EmpresaRepositorio, tags = ["empresas"])
@version(1, 0)
async def crear_empresa(empE: EmpresaEntrada):
    itemEmpresa = EmpresaRepositorio (id= str(uuid.uuid4()), nombre = empE.nombre, pais = empE.pais, ciudad = empE.ciudad)
    resultadoDB =  coleccion.insert_one(itemEmpresa.dict())
    return itemEmpresa

@app.post("/empresas", response_model=EmpresaRepositorio, tags = ["empresas"])
@version(2, 0)
async def crear_empresav2(empE: EmpresaEntradaV2):
    itemEmpresa = EmpresaRepositorio (id= str(uuid.uuid4()), nombre = empE.nombre, pais = empE.pais, ciudad = empE.ciudad, identificacion = empE.identificacion)
    resultadoDB =  coleccion.insert_one(itemEmpresa.dict())
    return itemEmpresa

@app.get("/empresas", response_model=List[EmpresaRepositorio], tags=["empresas"])
@version(1, 0)
def get_empresas(credentials: HTTPBasicCredentials = Depends(security)):
    authenticate(credentials)
    items = list(coleccion.find())
    print (items)
    return items

@app.get("/empresas/{empresa_id}", response_model=EmpresaRepositorio , tags=["empresas"])
@version(1, 0)
def obtener_empresa (empresa_id: str):
    item = coleccion.find_one({"id": empresa_id})
    if item:
        return item
    else:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

@app.delete("/empresas/{empresa_id}", tags=["empresas"])
@version(1, 0)
def eliminar_empresa (empresa_id: str):
    result = coleccion.delete_one({"id": empresa_id})
    if result.deleted_count == 1:
        return {"mensaje": "Empresa eliminada exitosamente"}
    else:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")

@app.get("/pista/{pista_id}", tags = ["artistas"])
@version(1, 0)
async def obtener_pista(pista_id: str):
    track = sp.track(pista_id)
    return track
    
@app.get("/artistas/{artista_id}", tags = ["artistas"])
@version(1, 0)
async def get_artista(artista_id: str):
    artista = sp.artist(artista_id)
    return artista


@app.get("/")
def read_root():
    return {"Hello": "Interoperabilidad 1"}

app = VersionedFastAPI(app)
