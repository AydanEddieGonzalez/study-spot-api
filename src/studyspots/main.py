from fastapi import FastAPI
from contextlib import asynccontextmanager
from studyspots.database import create_db_and_tables




@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield




app = FastAPI(title='Study Spot API', lifespan=lifespan)


@app.get('/health')
def health():
    return {'status': 'ok'}

