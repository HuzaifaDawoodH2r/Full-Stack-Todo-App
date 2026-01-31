from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine('postgresql+asyncpg://neondb_owner:npg_nv5KFlYS9EoD@ep-weathered-hat-ahm7gfnp-pooler.c-3.us-east-1.aws.neon.tech/neondb', echo=True)
