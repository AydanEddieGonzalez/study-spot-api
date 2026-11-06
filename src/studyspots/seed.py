import json
from pathlib import Path

from sqlmodel import Session, select

from studyspots.database import create_db_and_tables, engine
from studyspots.models import Rating, RatingCreate, Spot, SpotCreate

SEED_FILE = Path(__file__).resolve().parents[2] / "data" / "seed_spots.json"


def seed():
    create_db_and_tables()
    with Session(engine) as session:
        if session.exec(select(Spot)).first() is not None:
            print("Database already has spots, skipping seed.")
            return

        data = json.loads(SEED_FILE.read_text())

        for item in data:
            ratings = item.pop("ratings", [])

            spot = Spot.model_validate(SpotCreate(**item))
            session.add(spot)
            session.flush()

            for r in ratings:
                rating = Rating.model_validate(RatingCreate(**r), update={"spot_id": spot.id})
                session.add(rating)

        session.commit()
        print(f"Seeded {len(data)} spots.")


if __name__ == "__main__":
    seed()