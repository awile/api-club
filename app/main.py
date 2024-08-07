from fastapi import FastAPI, Depends, Request
from app.db import get_db_session

from sqlalchemy import text

app = FastAPI()


@app.middleware("http")
async def handle_db_session(request: Request, call_next):
    try:
        request.state.session = None
        response = await call_next(request)
        if request.state.session is not None:
            await request.state.session.commit()
    except Exception as err:
        if request.state.session is not None:
            await request.state.session.rollback()
        raise err
    finally:
        if request.state.session is not None:
            await request.state.session.close()

    return response


@app.get("/")
def status():
    return {"status": "ok"}


@app.get("/db-check")
async def test_db(session=Depends(get_db_session)):
    resp = await session.execute(text("SELECT 1"))
    return {"results": [row[0] for row in resp.all()]}
