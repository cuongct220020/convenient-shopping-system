# user-service/app/schemas/user_tag_schema.py
from typing import List, Dict, Optional
from pydantic import field_validator, Field
from sanic_ext.extensions.openapi import openapi

from shopping_shared.schemas.base_schema import BaseSchema


def validate_tag_format(tag_value: str) -> str:
    """Helper to validate 4-digit tag code format."""
    if not tag_value.isdigit() or len(tag_value) != 4:
        raise ValueError(
            f"Invalid tag_value format: {tag_value}. "
            f"Must be 4-digit code (e.g., '0212')"
        )
    return tag_value


@openapi.component
class UserTagBulkAddSchema(BaseSchema):
    """Schema for adding multiple tags to user."""
    tag_values: List[str] = Field(
        ...,
        description="List of tag codes to add",
        examples=[["0102", "0212", "0302"]],
        min_length=1,
        max_length=50  # Limit number of tags at once
    )

    @field_validator("tag_values")
    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        """Validate tag values uniqueness and format."""
        if len(v) != len(set(v)):
            raise ValueError("Duplicate tag values are not allowed")

        for tag in v:
            validate_tag_format(tag)
        return v

@openapi.component
class UserTagDeleteSchema(BaseSchema):
    """Schema for deleting tags from user."""
    tag_values: List[str] = Field(
        ...,
        description="List of tag codes to delete",
        examples=[["0102", "0212"]],
        min_length=1,
        max_length=50  # Limit number of tags at once
    )

    @field_validator("tag_values")
    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        """Validate tag format."""
        for tag in v:
            validate_tag_format(tag)
        return v


@openapi.component
class UserTagUpdateByCategorySchema(BaseSchema):
    """
    Schema for updating all tags in a specific category.
    Replaces all existing tags in the category with new ones.
    """
    category: str = Field(
        ...,
        description="Tag category to update",
        examples=["age", "medical", "allergy", "diet", "taste"]
    )
    tag_values: List[str] = Field(
        ...,
        description="List of tag values to set for this category (empty list removes all)",
        examples=[["0102", "0103"]],
        max_length=20  # Limit number of tags in a category
    )

    @field_validator('category')
    @classmethod
    def validate_category(cls, v: str) -> str:
        """Validate category is one of the allowed values."""
        allowed_categories = {'age', 'medical', 'allergy', 'diet', 'taste'}
        if v not in allowed_categories:
            raise ValueError(
                f"Category must be one of {allowed_categories}, got '{v}'"
            )
        return v

    @field_validator('tag_values')
    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        """Validate tag values are formatted correctly."""
        for tag in v:
            validate_tag_format(tag)
        return v


@openapi.component
class UserTagSchema(BaseSchema):
    """Schema for individual tag response."""
    id: int = Field(
        ...,
        description="The unique identifier of the tag",
        examples=[1]
    )
    tag_value: str = Field(
        ...,
        description="The tag code value",
        examples=["0102"]
    )
    tag_category: str = Field(
        ...,
        description="The category of the tag",
        examples=["age", "medical", "allergy", "diet", "taste"]
    )
    tag_name: str = Field(
        ...,
        description="The name of the tag",
        examples=["Adult", "Diabetes", "Dairy Allergy"]
    )
    description: Optional[str] = Field(
        None,
        description="The description of the tag",
        examples=["Adult age group", "Diabetes condition", "Dairy allergy"]
    )
    created_at: Optional[str] = Field(
        None,
        description="The creation timestamp of the tag",
        examples=["2023-01-01T00:00:00Z"]
    )


@openapi.component
class UserTagsByCategorySchema(BaseSchema):
    """Schema for grouping user tags by category."""
    age: List[UserTagSchema] = Field(
        default_factory=list,
        description="Age group tags (01xx)",
        examples=[[{
            "id": 1,
            "tag_value": "0102",
            "tag_category": "age",
            "tag_name": "Adult",
            "description": "Adult age group"
        }]]
    )
    medical: List[UserTagSchema] = Field(
        default_factory=list,
        description="Medical condition tags (02xx)",
        examples=[[{
            "id": 2,
            "tag_value": "0212",
            "tag_category": "medical",
            "tag_name": "Diabetes",
            "description": "Diabetes condition"
        }]]
    )
    allergy: List[UserTagSchema] = Field(
        default_factory=list,
        description="Allergy tags (03xx)",
        examples=[[{
            "id": 3,
            "tag_value": "0302",
            "tag_category": "allergy",
            "tag_name": "Dairy Allergy",
            "description": "Dairy allergy"
        }]]
    )
    diet: List[UserTagSchema] = Field(
        default_factory=list,
        description="Special diet tags (04xx)",
        examples=[[{
            "id": 4,
            "tag_value": "0401",
            "tag_category": "diet",
            "tag_name": "Vegetarian",
            "description": "Vegetarian diet"
        }]]
    )
    taste: List[UserTagSchema] = Field(
        default_factory=list,
        description="Taste preference tags (05xx)",
        examples=[[{
            "id": 5,
            "tag_value": "0501",
            "tag_category": "taste",
            "tag_name": "Spicy",
            "description": "Prefers spicy food"
        }]]
    )


@openapi.component
class UserTagsResponseSchema(BaseSchema):
    """Enhanced response schema for user tags."""
    data: UserTagsByCategorySchema = Field(
        ...,
        description="The categorized user tags"
    )
    total_tags: int = Field(
        ...,
        description="Total number of tags",
        examples=[5]
    )
    categories_count: Dict[str, int] = Field(
        ...,
        description="Count of tags in each category",
        examples=[{"age": 1, "medical": 1, "allergy": 1, "diet": 1, "taste": 1}]
    )


@openapi.component
class BulkTagOperationResponseSchema(BaseSchema):
    """Response schema for bulk tag operations."""
    success_count: int = Field(
        ...,
        description="Number of tags processed successfully",
        examples=[3]
    )
    failed_count: int = Field(
        ...,
        description="Number of tags that failed to process",
        examples=[0]
    )
    errors: List[Dict[str, str]] = Field(
        default=[],
        description="List of errors that occurred during processing",
        examples=[[{"tag_value": "0102", "error": "Invalid tag format"}]]
    )
    processed_tags: List[UserTagSchema] = Field(
        default=[],
        description="List of tags that were processed successfully",
        examples=[[{
            "id": 1,
            "tag_value": "0102",
            "tag_category": "age",
            "tag_name": "Adult",
            "description": "Adult age group"
        }]]
    )