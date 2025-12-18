"""Authentication package"""

from .security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_token,
    get_current_user,
    get_current_active_user,
    create_api_key,
    verify_api_key
)

from .rbac import (
    Role,
    Permission,
    get_role_permissions,
    has_permission,
    require_role,
    require_permission
)

__all__ = [
    'verify_password',
    'get_password_hash',
    'create_access_token',
    'create_refresh_token',
    'verify_token',
    'get_current_user',
    'get_current_active_user',
    'create_api_key',
    'verify_api_key',
    'Role',
    'Permission',
    'get_role_permissions',
    'has_permission',
    'require_role',
    'require_permission'
]
