

class UserAdminCreateSchema(UserCreateSchema):
    """Schema for admins to create a new user."""
    system_role: UserRole = UserRole.USER
