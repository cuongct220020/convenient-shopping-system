import json
import uuid
from sqlalchemy.orm import Session
from typing import List, Dict
from math import tanh
import heapq
from core.caching import redis_manager
from models.recipe_component import RecipesFlattened
from models.group_preference import GroupPreference, TagRelation
from models.component_existence import ComponentExistence
from schemas.ingredient_schemas import IngredientResponse


class Recommender:
    """
        Recommend recipes based on ingredient availability and tag preferences.
    """
    def __init__(self, db: Session):
        self.cache_ttl_seconds = 8 * 60 * 60
        self.top_k = 5
        self.positive_relations: Dict[str, int] = {}
        self.negative_relations: Dict[str, int] = {}
        self._load_tag_relation_dict(db)
    
    def _load_tag_relation_dict(self, db: Session):
        tag_relations = db.query(TagRelation).all()
        for relation in tag_relations:
            ingredient_idx = int(relation.ingredient_tag[1:])
            user_tag = relation.user_tag

            if relation.relation:
                if user_tag not in self.positive_relations:
                    self.positive_relations[user_tag] = 0
                self.positive_relations[user_tag] |= (1 << ingredient_idx)
            else:
                if user_tag not in self.negative_relations:
                    self.negative_relations[user_tag] = 0
                self.negative_relations[user_tag] |= (1 << ingredient_idx)

    def _tags_to_bitmap(self, tag_set: set[str]) -> int:
        bitmap = 0
        for tag in tag_set:
            idx = int(tag[1:])
            bitmap |= (1 << idx)
        return bitmap

    def calculate_tag_points(self, recipe_tag_set: set[str], group_tag_set: set[str]) -> int:
        recipe_bitmap = self._tags_to_bitmap(recipe_tag_set)

        total_points = 0

        for user_tag in group_tag_set:
            if user_tag in self.positive_relations:
                matches = recipe_bitmap & self.positive_relations[user_tag]
                total_points += bin(matches).count('1')
            if user_tag in self.negative_relations:
                mismatches = recipe_bitmap & self.negative_relations[user_tag]
                total_points -= 10 * bin(mismatches).count('1')

        return total_points

    async def recommend(self, db: Session, group_id: uuid.UUID) -> List[int]:
        cache_key = f"recipe:recommendations:{group_id}"

        try:
            cached = await redis_manager.client.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception:
            cached = None

        group_preferences = db.query(GroupPreference).filter(
            GroupPreference.group_id == group_id
        ).all()
        group_tag_set: set[str] = set()
        for pref in group_preferences:
            if pref.user_tag_list:
                group_tag_set.update(pref.user_tag_list)                                                        # type: ignore

        component_existence = db.query(ComponentExistence).filter(
            ComponentExistence.group_id == group_id
        ).first()
        component_name_set = set(component_existence.component_name_list) if component_existence else set()     # type: ignore

        recipes_flattened_list = db.query(RecipesFlattened).all()

        recipe_scores: list[tuple[float, int]] = []

        for recipes_flattened in recipes_flattened_list:
            ingredient_name_set: set[str] = set()
            recipe_tag_set: set[str] = set()

            for ingredient_data in recipes_flattened.all_ingredients:
                ingredient_dict = ingredient_data.get("ingredient")
                if not ingredient_dict:
                    continue

                name = ingredient_dict.get("component_name")
                if name:
                    ingredient_name_set.add(name)

                tags = ingredient_dict.get("ingredient_tag_list")
                if tags:
                    recipe_tag_set.update(tags)

            exist_points = len(ingredient_name_set & component_name_set)
            tag_points = self.calculate_tag_points(recipe_tag_set, group_tag_set)

            total_point = tanh(exist_points) + tanh(tag_points)

            if len(recipe_scores) < self.top_k:
                heapq.heappush(recipe_scores, (total_point, recipes_flattened.component_id))
            else:
                if total_point > recipe_scores[0][0]:
                    heapq.heapreplace(recipe_scores, (total_point, recipes_flattened.component_id))

        top_recipe_ids = [
            recipe_id for _, recipe_id in sorted(recipe_scores, reverse=True)
        ]

        try:
            await redis_manager.client.set(
                cache_key,
                json.dumps(top_recipe_ids),
                ex=self.cache_ttl_seconds
            )
        except Exception:
            pass

        return top_recipe_ids

