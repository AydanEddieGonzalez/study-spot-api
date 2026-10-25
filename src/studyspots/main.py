from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Session, select

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

@app.get('/spots', response_model=list[SpotRead])
def list_spots(session: Session = Depends(get_session)):
    spots = session.exec(select(Spot)).all()
    return spots

@app.get('/spots/{spot_id}', response_model=SpotRead)
def get_spot(spot_id: int, session: Session = Depends(get_session)):
    spot = session.get(Spot, spot_id)
    if spot is None:
        raise HTTPException(status_code=404, detail='Spot not found')
    return spot