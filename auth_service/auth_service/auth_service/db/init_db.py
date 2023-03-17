import pathlib

from asyncpg import Connection, UndefinedFunctionError
from loguru import logger
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine

from auth_service import crud, schemas
from auth_service.core.config import get_app_settings
from auth_service.db.session import Base, database_master
from auth_service.db.session import SessionLocal
from auth_service.db.session import engines
from auth_service.models.user_role import UserRole


async def truncate_tables(conn: Connection):
    q = f"""select truncate_tables_where_owner('postgres')"""
    logger.info("truncate_tables_where_owner('postgres')")
    try:
        await conn.execute(q)
    except UndefinedFunctionError:
        pass


async def execute_ddl(
    path: pathlib.Path,
    conn: Connection,
):
    try:
        with open(path, encoding="utf-8") as rf:
            sql = rf.read()
            res = await conn.execute(sql)
            if get_app_settings().DEBUG:
                logger.opt(colors=True).debug(
                    f"{path.name}: \n<fg 255,109,10>{sql}</fg 255,109,10>"
                )
            else:
                logger.info(f"{path.name}")
    except Exception as e:
        logger.error(f"{path.name}: {e.args}")


async def drop_all_models(_engine: dict[str, AsyncEngine]):
    for name, eng in _engine.items():
        if eng:
            async with eng.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all, checkfirst=True)
                logger.info(f"metadata.drop_all, engine: {name}")


async def create_all_models(_engine: dict[str, AsyncEngine]):
    for name, eng in _engine.items():
        if eng:
            async with eng.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
                logger.info(f"metadata.create_all, engine: {name}")


async def remove_first_superuser(db: AsyncSession):
    await crud.user.remove(
        db,
        email=get_app_settings().FIRST_SUPERUSER_EMAIL,
    )


async def create_first_superuser(db: AsyncSession):
    super_user = await crud.user.get_by_email(
        db,
        email=get_app_settings().FIRST_SUPERUSER_EMAIL,
    )
    if not super_user:
        user_in_admin = schemas.UserCreate(
            email=EmailStr(get_app_settings().FIRST_SUPERUSER_EMAIL),
            password=get_app_settings().FIRST_SUPERUSER_PASSWORD,
            password_confirm=get_app_settings().FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
            is_verified=True,
            full_name=get_app_settings().FIRST_SUPERUSER_FULLNAME,
            username=get_app_settings().FIRST_SUPERUSER_USERNAME,
            role=UserRole.admin,
        )
        super_user = await crud.user.create(db, obj_in=user_in_admin)
        logger.info("created")
    else:
        logger.info("first superuser already exists")
    return super_user


async def execute_sql_files(
    conn: Connection,
    path_to_sql_dir=pathlib.Path(__file__).parent.__str__() + "/sql",
):
    for sql_f in pathlib.Path(path_to_sql_dir).iterdir():
        if not sql_f.is_dir() and not sql_f.name.startswith("_"):
            await execute_ddl(sql_f, conn)


async def init_db():
    connection: Connection = await database_master.get_connection()
    await create_all_models(engines)
    await execute_sql_files(connection)
    async with SessionLocal() as db:
        await create_first_superuser(db)
    await connection.close()
