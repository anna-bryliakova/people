from fastapi import FastAPI
from routers import people
from log import log_middleware


app = FastAPI()

app_v1 = FastAPI()
app.mount("/v1", app_v1)

app.middleware("http")(log_middleware)

app_v1.include_router(people.router)



# Задание
#
# Реализовать API для сервиса «Генеологическое дерево» с использованием django + drf. В качестве БД использовать PostgreSQL
#
# Таблицы БД:
# 1. people
#     * id (primary key)
#     * first_name
#     * last_name
#     * mother_id (fk to people)
#     * father_id (fk to people)
#
# API:
# 1. GET /v1/people - получение списка людей
# 2. POST /v1/people - добавление человека
# 3. GET /v1/people/<person_id> - получение информации о человеке
# 4. PUT /v1/people/<person_id> - изменение
# 5. GET /v1/people/<person_id>/ancestors - получение родословной. Принимает опциональный параметр depth (в url) - количество возвращаемых поколений. Например, при depth=2, из API вернутся мать / отец / мать матери / отец матери / мать отца / отец отца. Если он не указан, то возвращаются все предки. Формат ответа:
# Задание со звёздочкой (если останется время)
#
# Настроить логирование и добавить в конфиг булевый параметр DUMP_SQL. Если он true, то необходимо в конце обработки каждого API-запроса писать в логи все sql-запросы + время их выполнения
