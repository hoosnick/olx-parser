from typing import List, Optional, Union

from pydantic.v1 import BaseModel


class Promotion(BaseModel):
    highlighted: Optional[bool] = None
    urgent: Optional[bool] = None
    top_ad: Optional[bool] = None
    options: List[str]
    b2c_ad_page: Optional[bool] = None
    premium_ad_page: Optional[bool] = None


class Value(BaseModel):
    value: Optional[int] = None
    type: Optional[str] = None
    arranged: Optional[bool] = None
    budget: Optional[bool] = None
    currency: Optional[str] = None
    negotiable: Optional[bool] = None
    converted_value: Optional[float] = None
    previous_value: Optional[str] = None
    converted_previous_value: Optional[str] = None
    converted_currency: Optional[str] = None
    label: Optional[str] = None
    key: Optional[Union[str, List[str]]] = None


class Param(BaseModel):
    key: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None
    value: Value


class User(BaseModel):
    id: Optional[int] = None
    created: Optional[str] = None
    other_ads_enabled: Optional[bool] = None
    name: Optional[str] = None
    logo: Optional[str] = None
    logo_ad_page: Optional[str] = None
    social_network_account_type: Optional[str] = None
    photo: Optional[str] = None
    banner_mobile: Optional[str] = None
    banner_desktop: Optional[str] = None
    company_name: Optional[str] = None
    about: Optional[str] = None
    b2c_business_page: Optional[bool] = None
    is_online: Optional[bool] = None
    last_seen: Optional[str] = None
    seller_type: Optional[str] = None
    uuid: Optional[str] = None


class Contact(BaseModel):
    name: Optional[str] = None
    phone: Optional[bool] = None
    chat: Optional[bool] = None
    negotiation: Optional[bool] = None
    courier: Optional[bool] = None


class Map(BaseModel):
    zoom: Optional[int] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    radius: Optional[int] = None
    show_detailed: Optional[bool] = None


class City(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    normalized_name: Optional[str] = None


class District(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None


class Region(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    normalized_name: Optional[str] = None


class Location(BaseModel):
    city: Optional[City] = City(id=1, name="Ташкент", normalized_name="")
    district: Optional[District] = District(id=1, name="Ташкент")
    region: Optional[Region] = Region(id=1, name="Ташкент", normalized_name="")


class Photo(BaseModel):
    id: Optional[int] = None
    filename: Optional[str] = None
    rotation: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    link: Optional[str] = None


class Category(BaseModel):
    id: Optional[int] = None
    type: Optional[str] = None


class Rock(BaseModel):
    offer_id: Optional[str] = None
    active: Optional[bool] = None
    mode: Optional[str] = None


class Delivery(BaseModel):
    rock: Rock


class Safedeal(BaseModel):
    weight: Optional[int] = None
    weight_grams: Optional[int] = None
    status: Optional[str] = None
    safedeal_blocked: Optional[bool] = None
    allowed_quantity: List


class Shop(BaseModel):
    subdomain: Optional[str] = None


class Offer(BaseModel):
    id: Optional[int] = None
    url: Optional[str] = None
    title: Optional[str] = None
    last_refresh_time: Optional[str] = None
    created_time: Optional[str] = None
    valid_to_time: Optional[str] = None
    pushup_time: Optional[str] = None
    description: Optional[str] = None
    promotion: Optional[Promotion] = None
    params: Optional[List[Param]] = None
    key_params: Optional[List] = None
    business: Optional[bool] = None
    user: Optional[User] = None
    status: Optional[str] = None
    contact: Optional[Contact] = None
    map: Optional[Map] = None
    location: Optional[Location] = None
    photos: Optional[List[Photo]] = None
    partner: Optional[str] = None
    category: Optional[Category] = None
    delivery: Optional[Delivery] = None
    safedeal: Optional[Safedeal] = None
    shop: Optional[Shop] = None
    offer_type: Optional[str] = None
