# notification-service/app/utils/get_group_info.py
from typing import Optional, List, Dict, Tuple
from uuid import UUID
import aiohttp
from shopping_shared.utils.logger_utils import get_logger

logger = get_logger("Group Info Utils")


def _get_user_service_url(config) -> str:
    """
    Lấy user service URL từ config.
    
    Args:
        config: App config object (có thể là từ request.app.config hoặc Config class)
    
    Returns:
        User service URL với /api/v1/user-service suffix
    """
    user_service_url = config.USER_SERVICE_URL if hasattr(config, 'USER_SERVICE_URL') else 'http://user-service:8000'
    # Thêm /api/v1/user-service suffix
    return f"{user_service_url}/api/v1/user-service"


async def get_group_info(
    group_id: UUID,
    config
) -> Tuple[Optional[str], List[Dict], Optional[Dict]]:
    """
    Lấy thông tin group bao gồm group_name, members, và head_chef từ user-service.
    
    Args:
        group_id: UUID của group
        config: App config object (từ request.app.config hoặc Config class)
    
    Returns:
        Tuple[group_name, members_list, head_chef_info]:
            - group_name: Tên của group hoặc None nếu có lỗi
            - members_list: List các dict chứa thông tin members (user info và role), empty list nếu có lỗi
            - head_chef_info: Dict chứa thông tin head chef (user info và role) hoặc None nếu không tìm thấy
    """
    user_service_url = _get_user_service_url(config)
    url = f"{user_service_url}/groups/{group_id}/members"
    
    headers = {}
    # Note: API này yêu cầu authentication, nhưng hiện tại chưa có service token
    # Có thể cần thêm authentication trong tương lai
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Parse response structure
                    group_data = data.get("data", {})
                    group_name = group_data.get("group_name")
                    members = group_data.get("members", []) or group_data.get("group_memberships", [])
                    
                    # Tìm head chef trong members
                    head_chef = None
                    for member in members:
                        if member.get("role") == "head_chef":
                            head_chef = member
                            break
                    
                    return group_name, members, head_chef
                elif response.status == 404:
                    logger.warning(f"Group {group_id} not found")
                    return None, [], None
                elif response.status == 403:
                    logger.warning(f"Permission denied accessing group {group_id}")
                    return None, [], None
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to get group info for {group_id}: {response.status} - {error_text}")
                    return None, [], None
                    
    except aiohttp.ClientError as e:
        logger.error(f"HTTP client error getting group info for {group_id}: {e}", exc_info=True)
        return None, [], None
    except Exception as e:
        logger.error(f"Unexpected error getting group info for {group_id}: {e}", exc_info=True)
        return None, [], None
