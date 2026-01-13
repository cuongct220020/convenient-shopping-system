import uuid
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Dict, Tuple
from math import tanh
import heapq
from cachetools import TTLCache
from models.recipe_component import Recipe
from models.group_preference import GroupPreference, TagRelation
from models.component_existence import ComponentExistence
from utils.custom_mapping import recipes_flattened_aggregated_mapping


class Recommender:
    """
        Recommend recipes based on ingredient availability and tag preferences.
    """
    def __init__(self, db: Session):
        self.cache: TTLCache[uuid.UUID, List[int]] = TTLCache(maxsize=1000, ttl=86400)
        self.tag_relation_dict: Dict[Tuple[str, str], int] = {}
        self._load_tag_relation_dict(db)
    
    def _load_tag_relation_dict(self, db: Session):
        """Load tag relations: (ingredient_tag, user_tag) -> 1 (match) or -10 (no match)."""
        tag_relations = db.query(TagRelation).all()
        self.tag_relation_dict = {}
        for relation in tag_relations:
            self.tag_relation_dict[(relation.ingredient_tag, relation.user_tag)] = 1 if relation.relation else -10
    
    def recommend(self, db: Session, group_id: uuid.UUID) -> List[int]:
        """Return top 10 recipe IDs for the given group_id."""
        if group_id in self.cache:
            return self.cache[group_id]

        group_preferences = db.query(GroupPreference).filter(
            GroupPreference.group_id == group_id
        ).all()
        group_tag_set: set[str] = set()
        for pref in group_preferences:
            if pref.user_tag_list:
                group_tag_set.update(pref.user_tag_list)                                # type: ignore

        component_existence = db.query(ComponentExistence).filter(
            ComponentExistence.group_id == group_id
        ).first()
        component_name_list = component_existence.component_name_list if component_existence else []
        component_name_list = set(component_name_list)

        recipes = db.execute(select(Recipe)).scalars().all()

        recipe_scores: List[Tuple[int, float]] = []
        
        for recipe in recipes:
            aggregated = recipes_flattened_aggregated_mapping([(1.0, recipe)])

            ingredient_name_list: set[str] = set()
            recipe_tag_list: set[str] = set()
            
            for _, ingredient in aggregated.all_ingredients.values():
                ingredient_name_list.add(ingredient.component_name)
                tags = ingredient.ingredient_tag_list
                if tags:
                    recipe_tag_list.update(tags)

            exist_points = len(ingredient_name_list & component_name_list)
            tag_points = sum(
                self.tag_relation_dict.get((ingredient_tag, user_tag), 0)
                for ingredient_tag in recipe_tag_list
                for user_tag in group_tag_set
            )

            total_point = tanh(exist_points) + tanh(tag_points)
            recipe_scores.append((recipe.component_id, total_point))

        top_10_recipe_ids = [recipe_id for recipe_id, _ in heapq.nlargest(10, recipe_scores, key=lambda x: x[1])]

        self.cache[group_id] = top_10_recipe_ids
        return top_10_recipe_ids

