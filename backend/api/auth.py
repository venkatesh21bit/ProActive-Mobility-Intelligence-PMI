"""
Authentication API for customer login with JWT
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

from data.database import get_db_session
from data.models import Customer, Vehicle
from auth.security import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    create_refresh_token,
    verify_token,
    get_current_user
)
from auth.rbac import Role

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: str
    address: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    customer_id: int
    email: str
    role: str


class LoginResponse(BaseModel):
    customer_id: int
    first_name: str
    last_name: str
    email: str
    phone: Optional[str]
    vehicle: Optional[dict] = None
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class CustomerResponse(BaseModel):
    customer_id: int
    first_name: str
    last_name: str
    email: str
    phone: Optional[str]
    address: Optional[str]
    vehicles: list



@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db_session)):
    """Register a new customer"""
    try:
        # Check if customer already exists
        query = select(Customer).where(Customer.email == request.email)
        result = await db.execute(query)
        existing_customer = result.scalar_one_or_none()
        
        if existing_customer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new customer with hashed password
        new_customer = Customer(
            email=request.email,
            password_hash=get_password_hash(request.password),
            first_name=request.first_name,
            last_name=request.last_name,
            phone=request.phone,
            address=request.address,
            role=Role.CUSTOMER.value
        )
        
        db.add(new_customer)
        await db.commit()
        await db.refresh(new_customer)
        
        # Generate tokens
        access_token = create_access_token(data={
            "sub": str(new_customer.customer_id),
            "email": new_customer.email,
            "role": new_customer.role
        })
        
        refresh_token = create_refresh_token(data={
            "sub": str(new_customer.customer_id)
        })
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            customer_id=new_customer.customer_id,
            email=new_customer.email,
            role=new_customer.role
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db_session)):
    """
    Authenticate customer with email and password
    """
    try:
        # Find customer by email
        query = select(Customer).where(Customer.email == request.email)
        result = await db.execute(query)
        customer = result.scalar_one_or_none()
        
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid email or password"
            )
        
        # Verify password (if password_hash exists)
        # Temporarily skip password verification for demo@pmi.com
        if request.email == "demo@pmi.com" and request.password == "demo123":
            # Allow demo login
            pass
        elif hasattr(customer, 'password_hash') and customer.password_hash:
            try:
                if not verify_password(request.password, customer.password_hash):
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid email or password"
                    )
            except Exception as e:
                # If password verification fails due to bcrypt issues, reject login
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
        else:
            # Legacy: For demo customers without password, just log them in
            # In production, require password for all users
            pass
        
        # Get customer's vehicle
        vehicle_query = select(Vehicle).where(Vehicle.customer_id == customer.customer_id)
        vehicle_result = await db.execute(vehicle_query)
        vehicle = vehicle_result.scalar_one_or_none()
        
        vehicle_data = None
        if vehicle:
            vehicle_data = {
                "vehicle_id": vehicle.vehicle_id,
                "vin": vehicle.vin,
                "make": vehicle.make,
                "model": vehicle.model,
                "year": vehicle.year,
                "mileage": vehicle.mileage
            }
        
        # Generate tokens
        access_token = create_access_token(data={
            "sub": str(customer.customer_id),
            "email": customer.email,
            "role": getattr(customer, 'role', Role.CUSTOMER.value)
        })
        
        refresh_token = create_refresh_token(data={
            "sub": str(customer.customer_id)
        })
        
        return LoginResponse(
            customer_id=customer.customer_id,
            first_name=customer.first_name,
            last_name=customer.last_name,
            email=customer.email,
            phone=customer.phone,
            vehicle=vehicle_data,
            access_token=access_token,
            refresh_token=refresh_token
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str, db: AsyncSession = Depends(get_db_session)):
    """Refresh access token using refresh token"""
    try:
        # Verify refresh token
        payload = verify_token(refresh_token, token_type="refresh")
        customer_id = payload.get("sub")
        
        # Get customer from database
        query = select(Customer).where(Customer.customer_id == int(customer_id))
        result = await db.execute(query)
        customer = result.scalar_one_or_none()
        
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        # Generate new access token
        access_token = create_access_token(data={
            "sub": str(customer.customer_id),
            "email": customer.email,
            "role": getattr(customer, 'role', Role.CUSTOMER.value)
        })
        
        # Generate new refresh token
        new_refresh_token = create_refresh_token(data={
            "sub": str(customer.customer_id)
        })
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            customer_id=customer.customer_id,
            email=customer.email,
            role=getattr(customer, 'role', Role.CUSTOMER.value)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Logout current user
    In production, invalidate token in Redis or database
    """
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=CustomerResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get current authenticated user's information"""
    customer_id = int(current_user.get("sub"))
    return await get_customer(customer_id, db)


@router.get("/customer/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: int, db: AsyncSession = Depends(get_db_session)):
    """Get customer details with their vehicles"""
    try:
        query = select(Customer).where(Customer.customer_id == customer_id)
        result = await db.execute(query)
        customer = result.scalar_one_or_none()
        
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )
        
        # Get customer's vehicles
        vehicle_query = select(Vehicle).where(Vehicle.customer_id == customer_id)
        vehicle_result = await db.execute(vehicle_query)
        vehicles = vehicle_result.scalars().all()
        
        vehicle_list = [
            {
                "vehicle_id": v.vehicle_id,
                "vin": v.vin,
                "make": v.make,
                "model": v.model,
                "year": v.year,
                "mileage": v.mileage
            }
            for v in vehicles
        ]
        
        return CustomerResponse(
            customer_id=customer.customer_id,
            first_name=customer.first_name,
            last_name=customer.last_name,
            email=customer.email,
            phone=customer.phone,
            address=customer.address,
            vehicles=vehicle_list
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get customer: {str(e)}"
        )
