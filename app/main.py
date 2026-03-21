from fastapi import FastAPI
import uvicorn
from app.routers import users,folders,ciphers
from app.database import engine, Base

app = FastAPI()

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(users.router)
app.include_router(folders.router)
app.include_router(ciphers.router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", reload=True)