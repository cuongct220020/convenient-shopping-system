# user-service/app/schemas/user_tag_schema.py
from typing import List
from pydantic import field_validator, Field
from shopping_shared.schemas.base_schema import BaseSchema


class UserTagBulkAddSchema(BaseSchema):
    """Schema for adding multiple tags to user."""
    tag_values: List[str] = Field(
        ...,
        description="List of tag codes to add",
        min_length=1
    )

    @field_validator("tag_values")
    @classmethod
    def validate_tag_values(cls, v: List[str]) -> List[str]:
        """Validate tag values."""
        if not v:
            raise ValueError("tag_values cannot be empty")

        # Check for duplicates
        if len(v) != len(set(v)):
            raise ValueError("Duplicate tag values are not allowed")

        # Validate format (4-digit codes)
        for tag_value in v:
            if not tag_value.isdigit() or len(tag_value) != 4:
                raise ValueError(
                    f"Invalid tag_value format: {tag_value}. "
                    f"Must be 4-digit code (e.g., '0212')"
                )

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
    def validate_tag_values(cls, v: List[str]) -> List[str]:
        """Validate tag values."""
        if not v:
            raise ValueError("tag_values cannot be empty")
        return v



# class UserTagsByCategoryResponseSchema(BaseSchema):
#     """Schema for grouping user tags by category."""
#     age: List[str] = Field(
#         default_factory=list,
#         description="Age group tags (01xx)"
#     )
#     medical: List[str] = Field(
#         default_factory=list,
#         description="Medical condition tags (02xx)"
#     )
#     allergy: List[str] = Field(
#         default_factory=list,
#         description="Allergy tags (03xx)"
#     )
#     diet: List[str] = Field(
#         default_factory=list,
#         description="Special diet tags (04xx)"
#     )
#     taste: List[str] = Field(
#         default_factory=list,
#         description="Taste preference tags (05xx)"
#     )

