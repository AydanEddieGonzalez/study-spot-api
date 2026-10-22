from enum import Enum
from sqlmodel import Field, SQLModel
from typing import Optional

class Noise(str, Enum):
    quiet = 'quiet'
    moderate = 'moderate'
    loud = 'loud'

class SpotBase(SQLModel):
    name: str = Field(min_length=1, max_length=100)
    location: str = Field(min_length=1, max_length=100)
    noise: Noise
    has_outlets: bool
    has_wifi: bool
    hours: Optional[str] = None

class Spot(SpotBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class SpotCreate(SpotBase):
    pass

class SpotUpdate(SQLModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    location: Optional[str] = Field(default=None, min_length=1, max_length=100)
    noise: Optional[Noise] = None
    has_outlets: Optional[bool] = None
    has_wifi: Optional[bool] = None
    hours: Optional[str] = None

class SpotRead(SpotBase):
    id: int