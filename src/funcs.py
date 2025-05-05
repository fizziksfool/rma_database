from datetime import datetime

from sqlalchemy import func

from .database import RMA, SessionLocal


def generate_rma_number() -> str:
    year_prefix = datetime.now().strftime('%y')
    base = int(year_prefix) * 1000

    with SessionLocal() as session:
        latest = (
            session.query(func.max(RMA.rma_number))
            .filter(RMA.rma_number.like(f'{year_prefix}%'))
            .scalar()
        )

        if latest:
            return str(int(latest) + 1)
        else:
            return str(base + 1)
