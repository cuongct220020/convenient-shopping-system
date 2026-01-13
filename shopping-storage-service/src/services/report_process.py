from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from schemas.plan_schemas import PlanReport
from schemas.storable_unit_schemas import StorableUnitCreate
from services.storable_unit_crud import StorableUnitCRUD
from models.storage import StorableUnit
from core.database import get_db
from shopping_shared.utils.logger_utils import get_logger

logger = get_logger("ReportProcess")

storable_unit_crud = StorableUnitCRUD(StorableUnit)

async def report_process(report: PlanReport):
    db = next(get_db())
    try:
        logger.info(f"Processing report with {len(report.report_content)} items")
        with db.begin():
            for item in report.report_content:
                storable_unit_data = StorableUnitCreate(
                    storage_id=item.storage_id,
                    package_quantity=item.package_quantity,
                    unit_name=item.unit_name,
                    component_id=item.component_id,
                    content_type=item.content_type,
                    content_quantity=item.content_quantity,
                    content_unit=item.content_unit,
                    expiration_date=item.expiration_date
                )
                await storable_unit_crud.create(db, storable_unit_data)
        logger.info(f"Successfully processed report with {len(report.report_content)} items")
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error processing report: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Integrity error: {str(e)}")
    except Exception as e:
        db.rollback()
        logger.error(f"Error processing report: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error processing report")
    finally:
        db.close()