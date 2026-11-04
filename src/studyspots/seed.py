import json
from pathlib import Path

from sqlmodel import Session, select

from studyspots.database import create_db_and_tables, engine
from studyspots.models import Rating, RatingCreate, Spot, SpotCreate

SEED_FILE = Path(__file__).resolve().parents[2] / "data" / "seed_spots.json"


