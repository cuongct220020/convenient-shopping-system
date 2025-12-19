from schemas.plan_schemas import PlanReport
from schemas.storable_unit_schemas import StorableUnitCreate
from services.storable_unit_crud import StorableUnitCRUD
from models.storage import StorableUnit
from database import SessionLocal

storable_unit_crud = StorableUnitCRUD(StorableUnit)

def report_process(report: PlanReport):
    db = SessionLocal()
    try:
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
            storable_unit_crud.create(db, storable_unit_data)
    finally:
        db.close()