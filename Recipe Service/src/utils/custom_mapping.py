from typing import Type
from schemas.recipe import RecipeDetailedResponse, ComponentDetailedBase
from schemas.ingredient import CountableIngredientResponse, UncountableIngredientResponse
from models.recipe_component import Recipe, ComponentList, RecipeComponent, CountableIngredient, UncountableIngredient

"""
    Recursive mapper for RecipeDetailedResponse
"""

ingredient_response_map: dict[Type[RecipeComponent], Type] = {
    CountableIngredient: CountableIngredientResponse,
    UncountableIngredient: UncountableIngredientResponse
}

def recipe_detailed_response_mapping(recipe: Recipe) -> RecipeDetailedResponse:
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
            default_servings=recipe.default_servings,
            instructions=recipe.instructions or [],
            component_list=[build_component_detail(cl) for cl in recipe.component_list]
        )

    return build_recipe_detail(recipe)