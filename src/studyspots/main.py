from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Session, select

from contextlib import asynccontextmanager
from studyspots.database import create_db_and_tables, get_session
from typing import Literal, Optional
from sqlmodel import Session, col, select
from studyspots.models import (
    Noise, Rating, RatingCreate, RatingRead,
    Spot, SpotCreate, SpotRead, SpotUpdate,
)



@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title='Study Spot API', lifespan=lifespan)


def to_spot_read(spot: Spot, session: Session) -> SpotRead:
    ratings = session.exec(select(Rating).where(Rating.spot_id == spot.id)).all()
    count = len(ratings)
    avg = sum(r.score for r in ratings) / count if count > 0 else None
    return SpotRead(**spot.model_dump(), avg_rating=avg, rating_count=count)


@app.get('/health')
def health():
    return {'status': 'ok'}

@app.post('/spots', response_model=SpotRead, status_code=201)
def create_spot(spot_in: SpotCreate, session: Session = Depends(get_session)):
    spot = Spot.model_validate(spot_in)
    session.add(spot)
    session.commit()
    session.refresh(spot)
    return to_spot_read(spot, session)

@app.get('/spots', response_model=list[SpotRead])
def list_spots(
    q: Optional[str] = None,
    noise: Optional[Noise] = None,
    outlets: Optional[bool] = None,
    wifi: Optional[bool] = None,
    session: Session = Depends(get_session),
    min_rating: Optional[float] = Query(default=None, ge=1, le=5),
    sort: Optional[Literal["rating", "name"]] = None,
):
    query = select(Spot)

    if q is not None:
        query = query.where(col(Spot.name).ilike(f"%{q}%"))
    if noise is not None:
        query = query.where(Spot.noise == noise)
    if outlets is not None:
        query = query.where(Spot.has_outlets == outlets)
    if wifi is not None:
        query = query.where(Spot.has_wifi == wifi )

    spots = session.exec(query).all()
    results = [to_spot_read(s, session) for s in spots]

    if min_rating is not None:
        results = [s for s in results if s.avg_rating is not None and s.avg_rating >= min_rating]

    if sort == "rating":
        results.sort(key=lambda s: s.avg_rating or 0, reverse=True)
    elif sort == "name":
        results.sort(key=lambda s: s.name.lower())

    return results

@app.get('/spots/{spot_id}', response_model=SpotRead)
def get_spot(spot_id: int, session: Session = Depends(get_session)):
    spot = session.get(Spot, spot_id)
    if spot is None:
        raise HTTPException(status_code=404, detail='Spot not found')
    return to_spot_read(spot, session)

@app.patch("/spots/{spot_id}", response_model=SpotRead)
def update_spot(spot_id: int, spot_in: SpotUpdate, session: Session = Depends(get_session)):
    spot = session.get(Spot, spot_id)
    if spot is None:
        raise HTTPException(status_code=404, detail="Spot not found")

    update_data = spot_in.model_dump(exclude_unset=True)
    spot.sqlmodel_update(update_data)


    session.add(spot)
    session.commit()
    session.refresh(spot)

    return to_spot_read(spot, session)

@app.delete("/spots/{spot_id}", status_code=204)
def delete_spot(spot_id: int, session: Session = Depends(get_session)):
    spot = session.get(Spot, spot_id)
    if spot is None:
        raise HTTPException(status_code=404, detail="Spot not found")

    ratings = session.exec(select(Rating).where(Rating.spot_id == spot_id)).all()
    for r in ratings:
        session.delete(r)
    
    session.delete(spot)
    session.commit()

@app.post("/spots/{spot_id}/ratings", response_model=RatingRead, status_code=201)
def create_rating(spot_id: int, rating_in: RatingCreate, session: Session = Depends(get_session)):
    spot = session.get(Spot, spot_id)
    if spot is None:
        raise HTTPException(status_code=404, detail="Spot not found")

    rating = Rating.model_validate(rating_in, update={"spot_id": spot_id})

    session.add(rating)
    session.commit()
    session.refresh(rating)
    return rating

@app.get("/spots/{spot_id}/ratings", response_model=list[RatingRead])
def list_ratings(spot_id: int, session: Session = Depends(get_session)):
    spot = session.get(Spot, spot_id)
    if spot is None:
        raise HTTPException(status_code=404, detail="Spot not found")

    ratings = session.exec(select(Rating).where(Rating.spot_id == spot_id)).all()
    return ratings
