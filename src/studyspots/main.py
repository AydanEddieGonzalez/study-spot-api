from fastapi import Depends, FastAPI
from sqlmodel import Session

from contextlib import asynccontextmanager
from studyspots.database import create_db_and_tables, get_session
from studyspots.models import Spot, SpotCreate, SpotRead



@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title='Study Spot API', lifespan=lifespan)


@app.get('/health')
def health():
    return {'status': 'ok'}

@app.post('/spots', response_model=SpotRead, status_code=201)
def create_spot(spot_in: SpotCreate, session: Session = Depends(get_session)):
    spot = Spot.model_validate(spot_in)
    session.add(spot)
    session.commit()
    session.refresh(spot)
    return spot