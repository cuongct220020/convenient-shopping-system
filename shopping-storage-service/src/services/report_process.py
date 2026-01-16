from typing import Dict, Optional
import uuid
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from schemas.plan_schemas import PlanReport
from enums.uc_measurement_unit import UCMeasurementUnit
from models.storage import StorableUnit, Storage
from core.database import SessionLocal
from core.messaging import kafka_manager
from shopping_shared.messaging.topics import COMPONENT_EXISTENCE_TOPIC
from shopping_shared.utils.logger_utils import get_logger

logger = get_logger("ReportProcess")

async def report_process(report: PlanReport):
    db = SessionLocal()
    try:
        logger.info(f"Processing report with {len(report.report_content)} items")

        storages_by_id: Dict[int, Storage] = {}
        group_id: Optional[uuid.UUID] = None
        has_component_units = False

        with db.begin():
            storage_ids = {item.storage_id for item in report.report_content}
            if storage_ids:
                storages = db.execute(
                    select(Storage).where(Storage.storage_id.in_(storage_ids))  # type: ignore[arg-type]
                ).scalars().all()
                storages_by_id = {s.storage_id: s for s in storages}

            for item in report.report_content:
                storage = storages_by_id.get(item.storage_id)
                if storage is None:
                    logger.warning(
                        f"Skipping report item: storage_id={item.storage_id} not found (plan_id={report.plan_id})"
                    )
                    continue

                # All units belong to the same group, so we just need to capture it once
                if group_id is None:
                    group_id = storage.group_id

                content_unit = None
                if item.content_unit is not None:
                    try:
                        content_unit = UCMeasurementUnit(str(item.content_unit).upper())
                    except ValueError:
                        logger.error(
                            "Skipping report item: invalid content_unit=%s (plan_id=%s, storage_id=%s, unit_name=%s)",
                            item.content_unit,
                            report.plan_id,
                            item.storage_id,
                            item.unit_name,
                            exc_info=True,
                        )
                        continue

                db.add(
                    StorableUnit(
                        storage_id=item.storage_id,
                        package_quantity=item.package_quantity,
                        unit_name=item.unit_name,
                        component_id=item.component_id,
                        content_type=item.content_type,
                        content_quantity=item.content_quantity,
                        content_unit=content_unit,
                        expiration_date=item.expiration_date,
                    )
                )

                # Track if any unit has component_id (ingredient)
                if item.component_id is not None:
                    has_component_units = True

        # Publish component existence update once for the group (after DB commit).
        if group_id is not None and has_component_units:
            try:
                stmt = (
                    select(StorableUnit.unit_name)
                    .join(Storage, StorableUnit.storage_id == Storage.storage_id)
                    .where(Storage.group_id == group_id)
                    .where(StorableUnit.component_id.isnot(None))
                    .distinct()
                )
                unit_names = db.execute(stmt).scalars().all()
                group_id_str = str(group_id)
                payload = {
                    "event_type": "update_component_existence",
                    "data": {
                        "group_id": group_id_str,
                        "unit_names": unit_names,
                    },
                }
                await kafka_manager.send_message(
                    topic=COMPONENT_EXISTENCE_TOPIC,
                    value=payload,
                    key=group_id_str,  # type: ignore[arg-type]
                    wait=True,
                )
                logger.info(f"Published component_existence update: group_id={group_id_str}")
            except Exception as e:
                logger.error(
                    f"Failed publishing component_existence update: group_id={str(group_id)}, err={str(e)}",
                    exc_info=True,
                )

        logger.info(f"Successfully processed report with {len(report.report_content)} items")
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error processing report: {str(e)}", exc_info=True)
        return
    except Exception as e:
        db.rollback()
        logger.error(f"Error processing report: {str(e)}", exc_info=True)
        return
    finally:
        db.close()