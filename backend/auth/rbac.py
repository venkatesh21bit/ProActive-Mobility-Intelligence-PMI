"""
Role-Based Access Control (RBAC)
"""

from enum import Enum
from typing import List, Optional
from fastapi import HTTPException, status, Depends
from .security import get_current_user


class Role(str, Enum):
    """User roles"""
    ADMIN = "admin"
    CUSTOMER = "customer"
    SERVICE_CENTER = "service_center"
    MECHANIC = "mechanic"
    VIEWER = "viewer"


class Permission(str, Enum):
    """System permissions"""
    # Customer permissions
    VIEW_OWN_VEHICLES = "view_own_vehicles"
    BOOK_APPOINTMENT = "book_appointment"
    VIEW_OWN_APPOINTMENTS = "view_own_appointments"
    CANCEL_OWN_APPOINTMENT = "cancel_own_appointment"
    
    # Service center permissions
    VIEW_ALL_APPOINTMENTS = "view_all_appointments"
    MANAGE_APPOINTMENTS = "manage_appointments"
    VIEW_CUSTOMER_DATA = "view_customer_data"
    
    # Mechanic permissions
    UPDATE_VEHICLE_STATUS = "update_vehicle_status"
    VIEW_ASSIGNED_TASKS = "view_assigned_tasks"
    
    # Admin permissions
    MANAGE_USERS = "manage_users"
    MANAGE_SERVICE_CENTERS = "manage_service_centers"
    VIEW_ANALYTICS = "view_analytics"
    MANAGE_SYSTEM_SETTINGS = "manage_system_settings"


# Role-Permission mapping
ROLE_PERMISSIONS = {
    Role.ADMIN: [
        Permission.MANAGE_USERS,
        Permission.MANAGE_SERVICE_CENTERS,
        Permission.VIEW_ANALYTICS,
        Permission.MANAGE_SYSTEM_SETTINGS,
        Permission.VIEW_ALL_APPOINTMENTS,
        Permission.MANAGE_APPOINTMENTS,
        Permission.VIEW_CUSTOMER_DATA,
    ],
    Role.CUSTOMER: [
        Permission.VIEW_OWN_VEHICLES,
        Permission.BOOK_APPOINTMENT,
        Permission.VIEW_OWN_APPOINTMENTS,
        Permission.CANCEL_OWN_APPOINTMENT,
    ],
    Role.SERVICE_CENTER: [
        Permission.VIEW_ALL_APPOINTMENTS,
        Permission.MANAGE_APPOINTMENTS,
        Permission.VIEW_CUSTOMER_DATA,
        Permission.UPDATE_VEHICLE_STATUS,
    ],
    Role.MECHANIC: [
        Permission.VIEW_ASSIGNED_TASKS,
        Permission.UPDATE_VEHICLE_STATUS,
    ],
    Role.VIEWER: [
        Permission.VIEW_OWN_VEHICLES,
        Permission.VIEW_OWN_APPOINTMENTS,
    ],
}


def get_role_permissions(role: Role) -> List[Permission]:
    """Get all permissions for a role"""
    return ROLE_PERMISSIONS.get(role, [])


def has_permission(user_role: Role, required_permission: Permission) -> bool:
    """Check if a role has a specific permission"""
    role_perms = get_role_permissions(user_role)
    return required_permission in role_perms


def require_role(*allowed_roles: Role):
    """
    Decorator to require specific roles
    
    Usage:
        @require_role(Role.ADMIN, Role.SERVICE_CENTER)
        async def admin_only_endpoint():
            pass
    """
    async def role_checker(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role")
        
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join([r.value for r in allowed_roles])}"
            )
        
        return current_user
    
    return role_checker


def require_permission(*required_permissions: Permission):
    """
    Decorator to require specific permissions
    
    Usage:
        @require_permission(Permission.MANAGE_USERS)
        async def manage_users_endpoint():
            pass
    """
    async def permission_checker(current_user: dict = Depends(get_current_user)):
        user_role_str = current_user.get("role")
        
        try:
            user_role = Role(user_role_str)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid user role"
            )
        
        user_permissions = get_role_permissions(user_role)
        
        for perm in required_permissions:
            if perm not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing required permission: {perm.value}"
                )
        
        return current_user
    
    return permission_checker
