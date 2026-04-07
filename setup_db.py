import psycopg2
import os
from urllib.parse import urlparse

# --- CONFIGURATION ---
# Format: postgresql://postgres:[YOUR-PASSWORD]@db.yoysnrzjgbsphvtwvzqs.supabase.co:5432/postgres
DB_URL = input("Enter your Supabase Connection String (from Settings > Database): ")

TABLES_SQL = """
-- Users Table
CREATE TABLE IF NOT EXISTS epay_users (
    "userId" SERIAL PRIMARY KEY,
    "fullName" TEXT NOT NULL,
    "emailId" TEXT UNIQUE NOT NULL,
    "phoneNumber" TEXT NOT NULL,
    "hashPassword" TEXT NOT NULL,
    "algoPassword" TEXT NOT NULL,
    "isActive" BOOLEAN DEFAULT TRUE,
    "createdOn" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "lastLoginOn" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Roles Table
CREATE TABLE IF NOT EXISTS epay_roles (
    "roleId" SERIAL PRIMARY KEY,
    "roleName" TEXT UNIQUE NOT NULL
);

-- User Roles Junction
CREATE TABLE IF NOT EXISTS epay_user_roles (
    "userRoleId" SERIAL PRIMARY KEY,
    "userId" INTEGER REFERENCES epay_users("userId"),
    "roleId" INTEGER REFERENCES epay_roles("roleId"),
    UNIQUE("userId", "roleId")
);

-- Business Types
CREATE TABLE IF NOT EXISTS epay_business_types (
    "businessTypeId" SERIAL PRIMARY KEY,
    "businessTypeName" TEXT UNIQUE NOT NULL,
    "isActive" BOOLEAN DEFAULT TRUE,
    "createdOn" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Business Table
CREATE TABLE IF NOT EXISTS epay_business (
    "businessId" SERIAL PRIMARY KEY,
    "businessName" TEXT UNIQUE NOT NULL,
    "businessTypeId" INTEGER REFERENCES epay_business_types("businessTypeId"),
    "userId" INTEGER REFERENCES epay_users("userId"),
    "businessLogo" TEXT,
    "businessAddress" TEXT,
    "businessCity" TEXT,
    "businessState" TEXT,
    "businessCountry" TEXT,
    "businessZip" TEXT,
    "businessPhone" TEXT,
    "businessEmail" TEXT,
    "businessWebsite" TEXT,
    "isActive" BOOLEAN DEFAULT TRUE,
    "templateStatus" TEXT DEFAULT 'MISSING',
    "createdOn" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Customers Table
CREATE TABLE IF NOT EXISTS epay_customers (
    "customerId" SERIAL PRIMARY KEY,
    "businessId" INTEGER REFERENCES epay_business("businessId"),
    "customerName" TEXT NOT NULL,
    "customerPhone" TEXT NOT NULL,
    "customerFullAddress" TEXT NOT NULL,
    "createdOn" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Invoices Table
CREATE TABLE IF NOT EXISTS epay_invoices (
    "invoiceId" SERIAL PRIMARY KEY,
    "businessId" INTEGER REFERENCES epay_business("businessId"),
    "customerId" INTEGER REFERENCES epay_customers("customerId"),
    "invoiceNumber" TEXT NOT NULL,
    "invoiceAmount" INTEGER NOT NULL,
    "amountInWords" TEXT NOT NULL,
    "paymentMode" TEXT NOT NULL,
    "paymentType" TEXT NOT NULL,
    "purpose" TEXT NOT NULL,
    "pdfURL" TEXT,
    "createdOn" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Subscription Plans
CREATE TABLE IF NOT EXISTS epay_subscription_plans (
    "subscriptionPlanId" SERIAL PRIMARY KEY,
    "subscriptionPlanName" TEXT NOT NULL,
    "subscriptionPlanDescription" TEXT NOT NULL,
    "subscriptionPlanPrice" INTEGER NOT NULL,
    "subscriptionPlanDuration" INTEGER NOT NULL,
    "subscriptionPlanStatus" BOOLEAN DEFAULT TRUE,
    "createdOn" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Subscriptions
CREATE TABLE IF NOT EXISTS epay_subscriptions (
    "subscriptionId" SERIAL PRIMARY KEY,
    "businessId" INTEGER REFERENCES epay_business("businessId") UNIQUE,
    "subscriptionPlanId" INTEGER REFERENCES epay_subscription_plans("subscriptionPlanId"),
    "subscriptionStatus" BOOLEAN DEFAULT TRUE,
    "subscriptionStartDate" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "subscriptionEndDate" TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    "autoRenew" BOOLEAN DEFAULT TRUE,
    "createdOn" TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
"""

def setup():
    try:
        print("Connecting to Supabase Database...")
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        
        print("Executing SQL to create tables...")
        cur.execute(TABLES_SQL)
        
        conn.commit()
        print("✅ Success! All tables have been created in Supabase.")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Error during setup: {str(e)}")

if __name__ == "__main__":
    setup()
