from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from jose import jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import requests

DATABASE_URL = "cockroachdb://appuser@10.68.32.4:26257/appdb?sslmode=disable"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

KEYCLOAK_URL = "http://10.68.32.149:8080"
REALM = "labRealm"
JWKS_URL = f"{KEYCLOAK_URL}/realms/{REALM}/protocol/openid-connect/certs"

app = FastAPI(title="Lab API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String)

Base.metadata.create_all(engine)

class ItemCreate(BaseModel):
    name: str
    description: str = ""

class ItemResponse(BaseModel):
    id: int
    name: str
    description: str
    class Config:
        from_attributes = True

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        jwks = requests.get(JWKS_URL).json()
        header = jwt.get_unverified_header(token)
        key = next(k for k in jwks["keys"] if k["kid"] == header["kid"])
        payload = jwt.decode(token, key, algorithms=["RS256"], options={"verify_aud": False})
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "API funcionando"}

@app.get("/dashboard")
def dashboard():
    return FileResponse("/opt/app/index.html")

@app.get("/items", response_model=list[ItemResponse])
def get_items(db: Session = Depends(get_db), user=Depends(verify_token)):
    return db.query(Item).all()

@app.post("/items", response_model=ItemResponse)
def create_item(item: ItemCreate, db: Session = Depends(get_db), user=Depends(verify_token)):
    db_item = Item(name=item.name, description=item.description)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.put("/items/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, item: ItemCreate, db: Session = Depends(get_db), user=Depends(verify_token)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    db_item.name = item.name
    db_item.description = item.description
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db), user=Depends(verify_token)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    db.delete(db_item)
    db.commit()
    return {"message": "Item eliminado"}

@app.get('/register')
def register_page():
    return FileResponse('/opt/app/register.html')

@app.get('/panel')
def panel_page():
    return FileResponse('/opt/app/dashboard.html')

@app.get("/register")
def register_page():
    return FileResponse("/opt/app/register.html")

@app.get("/panel")
def panel_page():
    return FileResponse("/opt/app/dashboard.html")

@app.get("/register")
def register_page():
    return FileResponse("/opt/app/register.html")

@app.get("/panel")
def panel_page():
    return FileResponse("/opt/app/dashboard.html")

from fastapi import Body

@app.post("/auth/register")
def register_user(data: dict = Body(...)):
    import requests as req
    # Obtener token de admin
    token_res = req.post(
        "http://10.68.32.149:8080/realms/master/protocol/openid-connect/token",
        data={"client_id":"admin-cli","username":"admin","password":"admin","grant_type":"password"}
    )
    admin_token = token_res.json().get("access_token")
    if not admin_token:
        raise HTTPException(status_code=500, detail="No se pudo autenticar como admin")

    # Crear usuario
    res = req.post(
        "http://10.68.32.149:8080/admin/realms/labRealm/users",
        headers={"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"},
        json={
            "username": data["usuario"],
            "email": data.get("email",""),
            "firstName": data.get("nombre",""),
            "lastName": data.get("apellido",""),
            "enabled": True,
            "emailVerified": True,
            "credentials": [{"type":"password","value":data["password"],"temporary":False}]
        }
    )
    if res.status_code == 201:
        return {"message": "Usuario creado exitosamente"}
    elif res.status_code == 409:
        raise HTTPException(status_code=409, detail="El usuario ya existe")
    else:
        raise HTTPException(status_code=res.status_code, detail=res.text)
