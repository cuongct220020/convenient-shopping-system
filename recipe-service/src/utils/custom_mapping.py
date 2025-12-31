from typing import Type
from schemas.recipe_flattened_schemas import AggregatedIngredientsResponse
from schemas.recipe_schemas import RecipeDetailedResponse, ComponentDetailedBase
from schemas.ingredient_schemas import CountableIngredientResponse, UncountableIngredientResponse, IngredientResponse
from models.recipe_component import Recipe, ComponentList, RecipeComponent, CountableIngredient, UncountableIngredient

"""
    Recursive mapper for RecipeDetailedResponse
"""

ingredient_response_map: dict[Type[RecipeComponent], Type] = {
    CountableIngredient: CountableIngredientResponse,
    UncountableIngredient: UncountableIngredientResponse
}

def recipe_detailed_mapping(recipe: Recipe) -> RecipeDetailedResponse:
    def build_component_detail(cl: ComponentList) -> ComponentDetailedBase:
        component: RecipeComponent = cl.component
        if isinstance(component, Recipe):
            return ComponentDetailedBase(
                quantity=cl.quantity,
                component=build_recipe_detail(component)
            )
        else:
            cls = ingredient_response_map.get(type(component))
            if cls is None:
                raise TypeError(f"Unknown ingredient type: {type(component)}")
            return ComponentDetailedBase(
                quantity=cl.quantity,
                component=cls.model_validate(component, from_attributes=True)           # type: ignore
            )

    def build_recipe_detail(recipe: Recipe) -> RecipeDetailedResponse:
        return RecipeDetailedResponse(
            component_id=recipe.component_id,
            component_name=recipe.component_name,
            type="recipe",
            level=recipe.level,
            default_servings=recipe.default_servings,
            instructions=recipe.instructions or [],
            keywords=recipe.keywords or [],
            component_list=[
                build_component_detail(cl)
                for cl in recipe.component_list
            ],
            image_url=recipe.image_url,
            prep_time=recipe.prep_time,
            cook_time=recipe.cook_time,
        )

    return build_recipe_detail(recipe)

def recipes_flattened_aggregated_mapping(recipes: list[tuple[float, Recipe]]) -> AggregatedIngredientsResponse:
    all_ingredients: dict[int, tuple[float, IngredientResponse]] = {}

    def process_component(component: RecipeComponent, multiplier: float):
        if isinstance(component, Recipe):
            multiplier /= component.default_servings
            for cl in component.component_list:
                process_component(cl.component, cl.quantity * multiplier)
        else:
            cls = ingredient_response_map.get(type(component))
            if cls is None:
                raise TypeError(f"Unknown ingredient type: {type(component)}")
            if component.component_id in all_ingredients:
                existing_quantity, ing_resp = all_ingredients[component.component_id]
                all_ingredients[component.component_id] = (existing_quantity + multiplier, ing_resp)
            else:
                ing_resp = cls.model_validate(component, from_attributes=True)          # type: ignore
                all_ingredients[component.component_id] = (multiplier, ing_resp)

    for quantity, recipe in recipes:
        process_component(recipe, quantity)

    return AggregatedIngredientsResponse(all_ingredients=all_ingredients)