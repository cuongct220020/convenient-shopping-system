# user-service/app/schemas/user_tag_schema.py
from typing import List
from pydantic import field_validator, Field
from shopping_shared.schemas.base_schema import BaseSchema


def validate_tag_format(tag_value: str) -> str:
    """Helper to validate 4-digit tag code format."""
    if not tag_value.isdigit() or len(tag_value) != 4:
        raise ValueError(
            f"Invalid tag_value format: {tag_value}. "
            f"Must be 4-digit code (e.g., '0212')"
        )
    return tag_value


class UserTagBulkAddSchema(BaseSchema):
    """Schema for adding multiple tags to user."""
    tag_values: List[str] = Field(
        ...,
        description="List of tag codes to add",
        min_length=1
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


class UserTagDeleteSchema(BaseSchema):
    """Schema for deleting tags from user."""
    tag_values: List[str] = Field(
        ...,
        description="List of tag codes to delete",
        min_length=1
    )

    @field_validator("tag_values")
    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        """Validate tag format."""
        for tag in v:
            validate_tag_format(tag)
        return v


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
        description="List of tag values to set for this category (empty list removes all)"
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


class UserTagsByCategorySchema(BaseSchema):
    """Schema for grouping user tags by category."""
    age: List[str] = Field(
        default_factory=list,
        description="Age group tags (01xx)"
    )
    medical: List[str] = Field(
        default_factory=list,
        description="Medical condition tags (02xx)"
    )
    allergy: List[str] = Field(
        default_factory=list,
        description="Allergy tags (03xx)"
    )
    diet: List[str] = Field(
        default_factory=list,
        description="Special diet tags (04xx)"
    )
    taste: List[str] = Field(
        default_factory=list,
        description="Taste preference tags (05xx)"
    )