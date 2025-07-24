"""Части рекурсивного запроса родословной и вспомогательные функции для получения данных и их обработки"""
from typing import Annotated, Literal

from fastapi import Depends, HTTPException, status
from sqlalchemy import select, text, Result, TextClause
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from config import settings
from log import logger

part_before_depth_use = '''
WITH RECURSIVE ancestors AS (
SELECT 
    id,
    first_name,
    last_name,
    mother_id,
    father_id,
    0 AS generation
FROM people
WHERE id = :person_id
UNION ALL
SELECT 
    p.id,
    p.first_name,
    p.last_name,
    p.mother_id,
    p.father_id,
    a.generation + 1
FROM people p
INNER JOIN ancestors a ON p.id = a.mother_id OR p.id = a.father_id
'''

part_depth_use = \
'''WHERE a.generation < :depth
'''

part_after_depth_use = \
''')
SELECT id, first_name, last_name, mother_id, father_id FROM ancestors
ORDER BY generation, id;
'''

async def get_object_or_404(db: Annotated[AsyncSession, Depends(get_db)], model, where_expression):
    instance = await db.scalar(select(model).where(where_expression))
    if not instance:
        raise HTTPException(
            detail=f"Запись в таблице {model.__tablename__} не найдена",
            status_code=status.HTTP_404_NOT_FOUND
        )
    return instance


def prepare_ancestors_params(person_id: int, depth: int | None) -> dict:
    """Возвращает параметры запроса"""
    params = {"person_id": person_id}
    if depth is not None:
        params |= {"depth": depth}
    return params


def prepare_ancestors_query(depth: int | None) -> TextClause:
    """Готовит запрос для выдачи родословной (полностью, если глубина поиска depth не указана,
    или же на указанную глубину"""
    query = text(part_before_depth_use + (
        part_depth_use + part_after_depth_use if depth is not None
        else part_after_depth_use))
    if settings.DUMP_SQL:
        logger.info(f"Запрос для поиска потомков: {query.compile()}")
    return query


def prepare_ancestors(result: Result, person_id: int) -> dict:
    """Приводит информацию о предках к нужному формату"""
    persons_dict = {dict_row["id"]: dict_row for dict_row in result.mappings()}
    ancestors = get_ancestors(person_id, persons_dict)
    for key_ in ("id", "first_name", "last_name"):
        ancestors.pop(key_)
    return ancestors


def get_ancestors(person_id: int, persons_dict: dict):
    """Рекурсивно ищет информацию о предках"""
    curr_person =  persons_dict[person_id]
    return {
        "id": person_id,
        "first_name": curr_person["first_name"],
        "last_name": curr_person["last_name"],
        "mother": get_ancestor_info(curr_person, persons_dict, "mother_id"),
        "father": get_ancestor_info(curr_person, persons_dict, "father_id")
    }


def get_ancestor_info(curr_person, persons_dict: dict, mode: Literal["mother_id", "father_id"]) -> dict | None:
    """Возвращает информацию о предке при её наличии"""
    return (None if (ancestor := curr_person[mode]) is None or not persons_dict.get(ancestor)
            else get_ancestors(ancestor, persons_dict))
