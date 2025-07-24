from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query,status
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.people import People
from schemas import CreatePerson
from utils import get_object_or_404, prepare_ancestors_params, prepare_ancestors_query, prepare_ancestors


router = APIRouter(prefix="/people", tags=["people"])


@router.get("/{person_id}/ancestors")
async def get_person_ancestors(
    db: Annotated[AsyncSession, Depends(get_db)],
    person_id: int,
    depth: Optional[int] = Query(None, ge=1, description="Глубина поиска (опционально)"),
):
    """Проверить наличие данных о человеке в базе и получить его родословную"""
    await get_object_or_404(db, People, People.id == person_id)
    params = prepare_ancestors_params(person_id, depth)
    query = prepare_ancestors_query(depth)
    result = await db.execute(query, params)
    return prepare_ancestors(result, person_id)


@router.get("/{person_id}")
async def get_person(db: Annotated[AsyncSession, Depends(get_db)], person_id: int):
    """Получить информацию о человеке"""
    return await get_object_or_404(db, People, People.id == person_id)


@router.get("/")
async def get_people(
    db: Annotated[AsyncSession, Depends(get_db)]):
    """Получить список людей"""
    people = await db.scalars(select(People))
    if people is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Людей не найдено")
    return {"result": people.all()}


@router.put("/{person_id}")
async def update_person(
    db: Annotated[AsyncSession, Depends(get_db)],
    person_id: int,
    person_data: CreatePerson
):
    """Обновить данные о человеке"""
    person = await get_object_or_404(db, People, People.id == person_id)
    person.first_name = person_data.first_name
    person.last_name = person_data.last_name
    person.mother_id = person_data.mother_id
    person.father_id = person_data.father_id
    await db.commit()
    return {"status_code": status.HTTP_200_OK, "transaction": f"Данные человека с id {person_id} обновлены"}


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_person(db: Annotated[AsyncSession, Depends(get_db)], create_person: CreatePerson):
    """Добавить человека"""
    await db.execute(
        insert(People).values(
            first_name=create_person.first_name,
            last_name=create_person.last_name,
            mother_id=create_person.mother_id,
            father_id=create_person.father_id,
        )
    )
    await db.commit()
    return {"status_code": status.HTTP_201_CREATED, "transaction": "Successful"}
