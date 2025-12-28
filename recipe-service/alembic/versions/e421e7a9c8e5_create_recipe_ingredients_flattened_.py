"""create recipe_ingredients_flattened materialized view

Revision ID: e421e7a9c8e5
Revises: 059653cddd90
Create Date: 2025-11-12 17:22:08.412071

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e421e7a9c8e5'
down_revision: Union[str, Sequence[str], None] = '059653cddd90'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop VIEW thường nếu có (từ lúc test)
    op.execute("DROP VIEW IF EXISTS recipe_ingredient_flattened CASCADE")

    # Tạo MATERIALIZED VIEW
    op.execute("""
        CREATE MATERIALIZED VIEW recipe_ingredient_flattened AS
        WITH RECURSIVE recipe_expansion AS (
            -- Base case: Lấy tất cả components trực tiếp từ recipes
            SELECT 
                cl.recipe_id,
                rc_recipe.component_name as recipe_name,
                cl.component_id,
                rc_component.component_name,
                rc_component.type as component_type,
                cl.quantity,
                r.default_servings,
                cl.quantity as adjusted_quantity,
                COALESCE(
                    ci.c_measurement_unit::text,
                    uci.uc_measurement_unit::text
                ) as measurement_unit,
                1 as level
            FROM component_lists cl
            INNER JOIN recipe_components rc_recipe ON cl.recipe_id = rc_recipe.component_id
            INNER JOIN recipe_components rc_component ON cl.component_id = rc_component.component_id
            INNER JOIN recipes r ON cl.recipe_id = r.component_id
            LEFT JOIN countable_ingredients ci ON cl.component_id = ci.component_id
            LEFT JOIN uncountable_ingredients uci ON cl.component_id = uci.component_id
            WHERE rc_recipe.type = 'recipe'

            UNION ALL

            -- Recursive case: Expand sub-recipes
            SELECT 
                re.recipe_id,
                re.recipe_name,
                cl.component_id,
                rc.component_name,
                rc.type as component_type,
                cl.quantity as original_quantity,
                r.default_servings,
                CASE 
                    WHEN r.default_servings > 0 THEN
                        re.adjusted_quantity * (cl.quantity / r.default_servings::float)
                    ELSE 
                        re.adjusted_quantity * cl.quantity
                END as adjusted_quantity,
                COALESCE(
                    ci.c_measurement_unit::text,
                    uci.uc_measurement_unit::text
                ) as measurement_unit,
                re.level + 1
            FROM recipe_expansion re
            INNER JOIN component_lists cl ON re.component_id = cl.recipe_id
            INNER JOIN recipe_components rc ON cl.component_id = rc.component_id
            INNER JOIN recipes r ON cl.recipe_id = r.component_id
            LEFT JOIN countable_ingredients ci ON cl.component_id = ci.component_id
            LEFT JOIN uncountable_ingredients uci ON cl.component_id = uci.component_id
            WHERE re.component_type = 'recipe'
            AND re.level < 10
        )
        , ingredient_totals AS (
            SELECT 
                recipe_id,
                recipe_name,
                component_id,
                component_name,
                component_type,
                measurement_unit,
                SUM(adjusted_quantity) as total_quantity
            FROM recipe_expansion
            WHERE component_type != 'recipe'
            GROUP BY recipe_id, recipe_name, component_id, component_name, component_type, measurement_unit
        )
        SELECT 
            recipe_id,
            recipe_name,
            jsonb_agg(
                jsonb_build_object(
                    'component_id', component_id,
                    'component_name', component_name,
                    'quantity', total_quantity,
                    'unit', measurement_unit,
                    'type', component_type
                ) ORDER BY component_name
            ) as all_ingredients
        FROM ingredient_totals
        GROUP BY recipe_id, recipe_name
    """)

    # Tạo UNIQUE INDEX trên recipe_id
    op.execute("""
               CREATE UNIQUE INDEX idx_recipe_ingredient_flattened_recipe_id
                   ON recipe_ingredient_flattened (recipe_id)
               """)

    # Tạo GIN INDEX cho JSONB column (để search nhanh)
    op.execute("""
               CREATE INDEX idx_recipe_ingredient_flattened_gin
                   ON recipe_ingredient_flattened USING gin(all_ingredients)
               """)


def downgrade() -> None:
    # Drop materialized view (indexes sẽ tự động drop theo CASCADE)
    op.execute("DROP MATERIALIZED VIEW IF EXISTS recipe_ingredient_flattened CASCADE")