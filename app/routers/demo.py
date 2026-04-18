from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.errors import ERROR_RESPONSES

router = APIRouter(prefix="/api/demo", tags=["Demo-SQLi"])


@router.get("/vulnerable-search", responses=ERROR_RESPONSES)
async def vulnerable_search(q: str = Query(...), db: AsyncSession = Depends(get_db)):
    # УЯЗВИМЫЙ КОД — для демонстрации. В прод-коде так делать нельзя.
    sql = f"SELECT id, email, name FROM users WHERE name = '{q}'"
    result = await db.execute(text(sql))
    rows = [dict(r._mapping) for r in result]
    return {"query": sql, "rows": rows}


@router.get("/safe-search", responses=ERROR_RESPONSES)
async def safe_search(q: str = Query(..., min_length=1, max_length=255),
                      db: AsyncSession = Depends(get_db)):
    # Безопасный код — параметризованный запрос.
    sql = text("SELECT id, email, name FROM users WHERE name = :q")
    result = await db.execute(sql, {"q": q})
    rows = [dict(r._mapping) for r in result]
    return {"rows": rows}
