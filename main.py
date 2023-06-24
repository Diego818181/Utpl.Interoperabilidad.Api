from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid

#seccion mongo importar libreria
import pymongo

import spotipy

sp = spotipy.Spotify(auth_manager=spotipy.oauth2.SpotifyClientCredentials(
    client_id='c8519595485648c3949369793de3e366',
    client_secret='d266e54ea24346a7b278445be87cd400'
))

description = """
Utpl tnteroperabilidad API ayuda a describir las capacidades de un directorio. 🚀

## Personas

Tu puedes crear una persona.
Tu puedes listar personas.


## Artistas

You will be able to:

* **Crear artista** (_not implemented_).
"""

tags_metadata = [
    {
        "name":"personas",
        "description": "Permite realizar un crud completo de una persona (listar)"
    }
]

app = FastAPI(
    title="Utpl Interoperabilidad APP 2",
    description= description,
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Felipe Quiñonez",
        "url": "http://x-force.example.com/contact/",
        "email": "fdquinones@utpl.edu.ec",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    openapi_tags = tags_metadata
)

#configuracion de mongo
cliente = pymongo.MongoClient("mongodb+srv://utplinteroperabilidad:0b1Fd3PFZZInSuZK@cluster0.susnphb.mongodb.net/?retryWrites=true&w=majority")
database = cliente["directorio"]
coleccion = database["persona"]

class PersonaRepositorio (BaseModel):
    id: str
    nombre: str
    edad: int
    ciudad: Optional[str] = None

class PersonaEntrada (BaseModel):
    nombre:str
    edad:int
    ciudad: Optional[str] = None


personaList = []

@app.post("/personas", response_model=PersonaRepositorio, tags = ["personas"])
async def crear_persona(personE: PersonaEntrada):
    itemPersona = PersonaRepositorio (id= str(uuid.uuid4()), nombre = personE.nombre, edad = personE.edad, ciudad = personE.ciudad)
    resultadoDB =  coleccion.insert_one(itemPersona.dict())
    return itemPersona

@app.get("/personas", response_model=List[PersonaRepositorio], tags=["personas"])
def get_personas():
    items = list(coleccion.find())
    print (items)
    return items

@app.get("/personas/{persona_id}", response_model=PersonaRepositorio , tags=["personas"])
def obtener_persona (persona_id: int):
    for persona in personaList:
        if persona.id == persona_id:
            return persona
    raise HTTPException(status_code=404, detail="Persona no encontrada")

@app.delete("/personas/{persona_id}", tags=["personas"])
def eliminar_persona (persona_id: int):
    persona = next((p for p in personaList if p.id == persona_id), None)
    if persona:
        personaList.remove(persona)
        return {"mensaje": "Persona eliminada exitosamente"}
    else:
        raise HTTPException(status_code=404, detail="Persona no encontrada")

@app.get("/pista/{pista_id}")
async def obtener_pista(pista_id: str):
    track = sp.track(pista_id)
    return track
    
@app.get("/artistas/{artista_id}")
async def get_artista(artista_id: str):
    artista = sp.artist(artista_id)
    return artista


@app.get("/")
def read_root():
    return {"Hello": "Interoperabilidad 8"}