class BaseNotificationTemplate:
    template_code: str
    title: str
    content: str
    data_fields: dict[str, type]

    @classmethod
    def validate_raw_data(cls, raw_data: dict) -> tuple[bool, list[str]]:
        errors = []

        for field, expected_type in cls.data_fields.items():
            if field not in raw_data:
                errors.append(f"Missing field: {field}")
            else:
                if not isinstance(raw_data[field], expected_type):
                    errors.append(
                        f"Field '{field}' must be {expected_type.__name__}, "
                        f"got {type(raw_data[field]).__name__}"
                    )

        return len(errors) == 0, errors

    @classmethod
    def render(cls, raw_data: dict) -> dict:
        is_valid, errors = cls.validate_raw_data(raw_data)
        if not is_valid:
            raise ValueError(
                f"Invalid raw_data for template '{cls.template_code}': {errors}"
            )

        return {
            "title": cls.title.format(**raw_data),
            "content": cls.content.format(**raw_data),
        }

class GroupUserAddedNotificationTemplate(BaseNotificationTemplate):
    template_code = "GROUP_USER_ADDED"
    title = "Chào mừng bạn gia nhập nhóm {group_name}!"
    content = "{requester_username} đã thêm bạn vào nhóm {group_name}. Hãy bắt đầu lên thực đơn ngay nhé!"
    data_fields = {
        "group_name": str,
        "requester_username": str
    }

class GroupUserRemovedNotificationTemplate(BaseNotificationTemplate):
    template_code = "GROUP_USER_REMOVED"
    title = "Bạn đã bị xóa khỏi nhóm {group_name}"
    content = "Bếp trưởng {requester_username} đã xóa bạn khỏi nhóm {group_name}."
    data_fields = {
        "group_name": str,
        "requester_username": str
    }

class GroupUserLeftNotificationTemplate(BaseNotificationTemplate):
    template_code = "GROUP_USER_LEFT"
    title = "Bạn đã rời khỏi nhóm {group_name}"
    content = "Bạn đã rời khỏi nhóm {group_name}."
    data_fields = {
        "group_name": str
    }

class GroupHeadChefUpdatedNotificationTemplate(BaseNotificationTemplate):
    template_code = "GROUP_HEAD_CHEF_UPDATED"
    title = "Bếp Trưởng mới cho nhóm {group_name}"
    content = "{new_head_chef_username} đã được chỉ định làm Bếp Trưởng mới cho nhóm {group_name} bởi {requester_username}."
    data_fields = {
        "group_name": str,
        "new_head_chef_username": str,
        "requester_username": str
    }

class FoodExpiringSoonNotificationTemplate(BaseNotificationTemplate):
    template_code = "FOOD_EXPIRING_SOON"
    title = "Thực phẩm sắp hết hạn!"
    content = "Thực phẩm '{unit_name}' trong {storage_name} của nhóm {group_name} sẽ hết hạn vào ngày {expiration_date}. Hãy sử dụng nó sớm nhé!"
    data_fields = {
        "unit_name": str,
        "storage_name": str,
        "group_name": str,
        "expiration_date": str
    }

class FoodExpiredNotificationTemplate(BaseNotificationTemplate):
    template_code = "FOOD_EXPIRED"
    title = "Thực phẩm đã hết hạn!"
    content = "Thực phẩm '{unit_name}' trong {storage_name} của nhóm {group_name} đã hết hạn. Hãy kiểm tra và xử lý nó nhé!"
    data_fields = {
        "unit_name": str,
        "storage_name": str,
        "group_name": str
    }

class PlanAssignedNotificationTemplate(BaseNotificationTemplate):
    template_code = "PLAN_ASSIGNED"
    title = "Kế hoạch mua sắm đã được giao!"
    content = "Kế hoạch mua sắm #{plan_id} (hạn chót: {deadline}) của nhóm {group_name} đã được đăng ký thực hiện bởi {assignee_username}."
    data_fields = {
        "plan_id": int,
        "deadline": str,
        "group_name": str,
        "assignee_username": str
    }

class PlanReportedNotificationTemplate(BaseNotificationTemplate):
    template_code = "PLAN_REPORTED"
    title = "Kế hoạch mua sắm đã hoàn thành!"
    content = "{assignee_username} đã hoàn thành Kế hoạch mua sắm #{plan_id} của nhóm {group_name}!"
    data_fields = {
        "plan_id": int,
        "assignee_username": str,
        "group_name": str
    }

class PlanExpiredNotificationTemplate(BaseNotificationTemplate):
    template_code = "PLAN_EXPIRED"
    title = "Kế hoạch mua sắm đã quá hạn!"
    content = "Kế hoạch mua sắm #{plan_id} của nhóm {group_name} đã quá hạn vào {deadline} mà chưa được hoàn thành."
    data_fields = {
        "plan_id": int,
        "group_name": str,
        "deadline": str
    }

class DailyMealNotificationTemplate(BaseNotificationTemplate):
    template_code = "DAILY_MEAL"
    title = "Thực đơn hôm nay cho nhóm {group_name}"
    content = (
        "Chào buổi sáng, Bếp Trưởng! Các bữa ăn đã được lên kế hoạch cho hôm nay:\n"
        "  +  Bữa sáng: {breakfast}\n"
        "  +  Bữa trưa: {lunch}\n"
        "  +  Bữa tối: {dinner}\n"
        "Chúc nhóm có một ngày ngon miệng và khỏe mạnh!"
    )

    data_fields = {
        "group_name": str,
        "breakfast": list[str],
        "lunch": list[str],
        "dinner": list[str],
    }

    @classmethod
    def _format_meal_list(cls, meals: list[str]) -> str:
        if not meals:
            return "Chưa có kế hoạch"
        return ", ".join(meals)

    @classmethod
    def render(cls, raw_data: dict) -> dict:
        is_valid, errors = cls.validate_raw_data(raw_data)
        if not is_valid:
            raise ValueError(
                f"Invalid raw_data for template '{cls.template_code}': {errors}"
            )

        formatted_data = {
            **raw_data,
            "breakfast": cls._format_meal_list(raw_data["breakfast"]),
            "lunch": cls._format_meal_list(raw_data["lunch"]),
            "dinner": cls._format_meal_list(raw_data["dinner"]),
        }

        return {
            "title": cls.title.format(**formatted_data),
            "content": cls.content.format(**formatted_data),
        }

