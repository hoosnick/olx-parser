from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class Base(BaseModel):
    model_config = ConfigDict(extra="ignore")


class Value(Base):
    label: Optional[str] = None


class Param(Base):
    key: Optional[str] = None
    value: Value


class Map(Base):
    lat: Optional[float] = None
    lon: Optional[float] = None


class City(Base):
    id: Optional[int] = None
    name: Optional[str] = None
    normalized_name: Optional[str] = None


class District(Base):
    id: Optional[int] = None
    name: Optional[str] = None


class Region(Base):
    id: Optional[int] = None
    name: Optional[str] = None
    normalized_name: Optional[str] = None


class Location(Base):
    city: Optional[City] = City(id=1, name="Ташкент", normalized_name="")
    district: Optional[District] = District(id=1, name="Ташкент")
    region: Optional[Region] = Region(id=1, name="Ташкент", normalized_name="")


class Photo(Base):
    link: Optional[str] = None


class Offer(Base):
    id: Optional[int] = None
    url: Optional[str] = None
    title: Optional[str] = None
    last_refresh_time: Optional[str] = None
    description: Optional[str] = None
    params: Optional[List[Param]] = None
    status: Optional[str] = None
    map: Optional[Map] = None
    location: Optional[Location] = None
    photos: Optional[List[Photo]] = None
