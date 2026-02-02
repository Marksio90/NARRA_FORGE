-- Migration: Add user system with subscriptions and credits
-- Date: 2026-01-27
-- Description: Add users table, subscription plans, and link projects to users

-- Create the SubscriptionTier ENUM type if it doesn't exist
-- Using UPPERCASE values to match SQLAlchemy enum name serialization
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'subscription_tier_enum') THEN
        CREATE TYPE subscription_tier_enum AS ENUM (
            'FREE',
            'PRO',
            'PREMIUM'
        );
    END IF;
END$$;

-- Create users table
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users') THEN
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            username VARCHAR(100) UNIQUE NOT NULL,
            hashed_password VARCHAR(255) NOT NULL,
            full_name VARCHAR(255),

            -- Subscription management
            subscription_tier subscription_tier_enum NOT NULL DEFAULT 'FREE',
            subscription_valid_until TIMESTAMP,
            stripe_customer_id VARCHAR(255),
            stripe_subscription_id VARCHAR(255),

            -- Credits system
            credits_remaining INTEGER NOT NULL DEFAULT 1,
            total_credits_purchased INTEGER NOT NULL DEFAULT 0,

            -- Usage tracking
            books_generated INTEGER NOT NULL DEFAULT 0,
            total_words_generated INTEGER NOT NULL DEFAULT 0,
            total_cost_incurred DECIMAL(10,2) NOT NULL DEFAULT 0.0,

            -- Account status
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            is_verified BOOLEAN NOT NULL DEFAULT FALSE,
            verification_token VARCHAR(255),
            password_reset_token VARCHAR(255),
            password_reset_expires TIMESTAMP,

            -- Timestamps
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            last_login TIMESTAMP
        );
    END IF;
END$$;

-- Create indexes for users table
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users') THEN
        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_users_email') THEN
            CREATE INDEX idx_users_email ON users(email);
        END IF;
        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_users_username') THEN
            CREATE INDEX idx_users_username ON users(username);
        END IF;
        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_users_stripe_customer') THEN
            CREATE INDEX idx_users_stripe_customer ON users(stripe_customer_id);
        END IF;
    END IF;
END$$;

-- Create subscription_plans table
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'subscription_plans') THEN
        CREATE TABLE subscription_plans (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) UNIQUE NOT NULL,
            tier subscription_tier_enum NOT NULL,

            -- Pricing
            price_monthly DECIMAL(10,2) NOT NULL,
            price_yearly DECIMAL(10,2) NOT NULL,

            -- Features
            books_per_month INTEGER NOT NULL,
            max_words_per_book INTEGER NOT NULL,
            series_support BOOLEAN NOT NULL DEFAULT FALSE,
            priority_generation BOOLEAN NOT NULL DEFAULT FALSE,
            cover_generation BOOLEAN NOT NULL DEFAULT FALSE,
            deep_editing BOOLEAN NOT NULL DEFAULT FALSE,
            all_export_formats BOOLEAN NOT NULL DEFAULT FALSE,

            -- Stripe
            stripe_price_id_monthly VARCHAR(255),
            stripe_price_id_yearly VARCHAR(255),

            -- Status
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            display_order INTEGER NOT NULL DEFAULT 0,

            -- Timestamps
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    END IF;
END$$;

-- Insert default subscription plans (only if table is empty)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'subscription_plans') THEN
        IF NOT EXISTS (SELECT 1 FROM subscription_plans WHERE name = 'Free') THEN
            INSERT INTO subscription_plans (
                name, tier, price_monthly, price_yearly,
                books_per_month, max_words_per_book,
                series_support, priority_generation, cover_generation,
                deep_editing, all_export_formats, is_active, display_order
            ) VALUES
            ('Free', 'FREE', 0, 0, 1, 50000, FALSE, FALSE, FALSE, FALSE, FALSE, TRUE, 1),
            ('Pro', 'PRO', 29.00, 290.00, 5, 150000, TRUE, FALSE, TRUE, TRUE, TRUE, TRUE, 2),
            ('Premium', 'PREMIUM', 79.00, 790.00, 999999, 200000, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, 3);
        END IF;
    END IF;
END$$;

-- Add user_id column to projects table
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'projects') THEN
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'projects' AND column_name = 'user_id') THEN
            ALTER TABLE projects ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE SET NULL;
        END IF;
    END IF;
END$$;

-- Create index for projects.user_id
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'projects') THEN
        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_projects_user_id') THEN
            CREATE INDEX idx_projects_user_id ON projects(user_id);
        END IF;
    END IF;
END$$;
