from __future__ import annotations
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    emailId: EmailStr
    fullName: Optional[str] = None
    phoneNumber: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    emailId: Optional[EmailStr] = None
    fullName: Optional[str] = None
    phoneNumber: Optional[str] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    userId: int
    isActive: bool
    createdOn: datetime
    roles: List[RoleResponse] = []
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    emailId: Optional[str] = None

class ForgotPassword(BaseModel):
    emailId: EmailStr

class ResetPassword(BaseModel):
    emailId: EmailStr
    currentPassword: str
    newPassword: str

# Role Schemas
class RoleBase(BaseModel):
    roleName: str

class RoleCreate(RoleBase):
    pass

class RoleResponse(RoleBase):
    roleId: int
    
    class Config:
        from_attributes = True

class UserRoleBase(BaseModel):
    userId: int
    roleId: int

class UserRoleResponse(UserRoleBase):
    userRoleId: int

    class Config:
        from_attributes = True

# Business Type Schemas
class BusinessTypeBase(BaseModel):
    businessTypeName: str
    isActive: bool = True

class BusinessTypeResponse(BusinessTypeBase):
    businessTypeId: int
    createdOn: datetime
    
    class Config:
        from_attributes = True

# Business Schemas
class BusinessBase(BaseModel):
    businessName: str
    businessTypeId: int
    userId: int
    businessLogo: Optional[str] = None
    businessAddress: Optional[str] = None
    businessCity: Optional[str] = None
    businessState: Optional[str] = None
    businessCountry: Optional[str] = None
    businessZip: Optional[str] = None
    businessPhone: Optional[str] = None
    businessEmail: Optional[str] = None
    businessWebsite: Optional[str] = None
    isActive: bool = True
    templateStatus: Optional[str] = "MISSING"

class BusinessCreate(BusinessBase):
    pass

class BusinessResponse(BusinessBase):
    businessId: int
    createdOn: datetime
    lastLoginOn: datetime
    
    class Config:
        from_attributes = True

# Customer Schemas
class CustomerBase(BaseModel):
    businessId: int
    customerName: str
    customerPhone: str
    customerFullAddress: str

class CustomerCreate(CustomerBase):
    pass

class CustomerResponse(CustomerBase):
    customerId: int
    createdOn: datetime
    
    class Config:
        from_attributes = True

# Invoice Schemas
class InvoiceBase(BaseModel):
    businessId: int
    customerId: int
    invoiceNumber: str
    invoiceAmount: int
    amountInWords: str
    paymentMode: str
    paymentType: str
    purpose: str
    pdfURL: Optional[str] = None
    BookNo: Optional[str] = None
    billCollector: Optional[str] = None
    Nazim: Optional[str] = None
    invoiceDate: Optional[str] = None

class InvoiceCreate(InvoiceBase):
    pass

class InvoiceResponse(InvoiceBase):
    invoiceId: int
    createdOn: datetime
    customerName: Optional[str] = None
    customerPhone: Optional[str] = None
    
    class Config:
        from_attributes = True

class InvoiceWithCustomerCreate(BaseModel):
    businessId: int
    invoiceNumber: str
    invoiceAmount: int
    amountInWords: str
    paymentMode: str
    paymentType: str
    purpose: str
    pdfURL: Optional[str] = None
    customerName: str
    customerPhone: str
    customerFullAddress: str
    BookNo: Optional[str] = None
    billCollector: Optional[str] = None
    Nazim: Optional[str] = None
    invoiceDate: Optional[str] = None

class DashboardStats(BaseModel):
    totalBusinesses: int
    totalInvoices: int
    pendingTemplates: int
    missingTemplates: int
    totalUsers: int

class InvoicePDFData(BaseModel):
    businessId: int
    invoiceNumber: str
    BookNo: str
    invoiceDate: str
    CustomerName: str
    amountinwords: str
    invoiceAmount: int
    purpose: str
    billCollector: str
    Nazim: str
    customerFullAddress: str
    customerPhone: str
    paymentMode: str
    paymentType: str

# Subscription Plan Schemas
class SubscriptionPlanBase(BaseModel):
    subscriptionPlanName: str
    subscriptionPlanDescription: str
    subscriptionPlanPrice: int
    subscriptionPlanDuration: int
    subscriptionPlanStatus: bool = True

class SubscriptionPlanCreate(SubscriptionPlanBase):
    pass

class SubscriptionPlanUpdate(BaseModel):
    subscriptionPlanName: Optional[str] = None
    subscriptionPlanDescription: Optional[str] = None
    subscriptionPlanPrice: Optional[int] = None
    subscriptionPlanDuration: Optional[int] = None
    subscriptionPlanStatus: Optional[bool] = None

class SubscriptionPlanResponse(SubscriptionPlanBase):
    subscriptionPlanId: int
    createdOn: datetime

    class Config:
        from_attributes = True

# Subscription Schemas
class SubscriptionBase(BaseModel):
    businessId: int
    subscriptionPlanId: int
    subscriptionStatus: bool = True
    subscriptionStartDate: datetime
    subscriptionEndDate: datetime
    autoRenew: bool = True

class SubscriptionCreate(SubscriptionBase):
    pass

class SubscriptionUpdate(BaseModel):
    subscriptionPlanId: Optional[int] = None
    subscriptionStatus: Optional[bool] = None
    subscriptionStartDate: Optional[datetime] = None
    subscriptionEndDate: Optional[datetime] = None
    autoRenew: Optional[bool] = None

class SubscriptionResponse(SubscriptionBase):
    subscriptionId: int
    createdOn: datetime

    class Config:
        from_attributes = True

# Subscription Payment Schemas
class SubscriptionPaymentBase(BaseModel):
    subscriptionId: int
    paymentStatus: bool = True
    paymentDate: datetime
    paymentAmount: int
    paymentMode: str
    paymentType: str
    paymentPurpose: str

class SubscriptionPaymentCreate(SubscriptionPaymentBase):
    pass

class SubscriptionPaymentUpdate(BaseModel):
    paymentStatus: Optional[bool] = None
    paymentDate: Optional[datetime] = None
    paymentAmount: Optional[int] = None
    paymentMode: Optional[str] = None
    paymentType: Optional[str] = None
    paymentPurpose: Optional[str] = None

class SubscriptionPaymentResponse(SubscriptionPaymentBase):
    subscriptionPaymentId: int
    createdOn: datetime

    class Config:
        from_attributes = True

# Subscription Usage Schemas
class SubscriptionUsageBase(BaseModel):
    subscriptionId: int
    usageMonth: str # YYYY-MM
    invoiceCount: int

class SubscriptionUsageCreate(SubscriptionUsageBase):
    pass

class SubscriptionUsageUpdate(BaseModel):
    invoiceCount: Optional[int] = None

class SubscriptionUsageResponse(SubscriptionUsageBase):
    subscriptionUsageId: int
    createdOn: datetime

    class Config:
        from_attributes = True
