-- Migration: Add publishing metadata support
-- Date: 2026-01-27
-- Description: Add publishing_metadata and sales_tracking tables for commercial book sales

-- Create publishing_metadata table
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'publishing_metadata') THEN
        CREATE TABLE publishing_metadata (
            id SERIAL PRIMARY KEY,
            project_id INTEGER UNIQUE NOT NULL REFERENCES projects(id) ON DELETE CASCADE,

            -- ISBN numbers
            isbn_13 VARCHAR(17) UNIQUE,
            isbn_10 VARCHAR(13) UNIQUE,
            asin VARCHAR(20),

            -- Categories
            primary_category VARCHAR(100),
            secondary_categories JSONB DEFAULT '[]'::jsonb,
            thema_codes JSONB DEFAULT '[]'::jsonb,

            -- Keywords
            keywords JSONB DEFAULT '[]'::jsonb,

            -- Pricing
            price_usd DECIMAL(10,2),
            price_eur DECIMAL(10,2),
            price_gbp DECIMAL(10,2),
            price_pln DECIMAL(10,2),

            -- Royalty
            royalty_type VARCHAR(20) DEFAULT '70_percent',
            kdp_select_enrolled BOOLEAN DEFAULT FALSE,

            -- Cover
            cover_image_url VARCHAR(500),
            cover_image_path VARCHAR(500),
            cover_designer VARCHAR(255),
            cover_generated_by_ai BOOLEAN DEFAULT FALSE,

            -- Marketing copy
            book_description TEXT,
            editorial_review TEXT,
            author_bio TEXT,
            tagline VARCHAR(255),

            -- Series info
            series_name VARCHAR(255),
            series_position INTEGER,

            -- Content ratings
            age_rating VARCHAR(20),
            content_warnings JSONB DEFAULT '[]'::jsonb,
            is_adult_content BOOLEAN DEFAULT FALSE,

            -- Publishing status
            is_published BOOLEAN DEFAULT FALSE,
            publication_date TIMESTAMP,
            first_publication_date TIMESTAMP,

            -- Copyright
            copyright_holder VARCHAR(255),
            copyright_year INTEGER,
            rights_territory VARCHAR(100) DEFAULT 'Worldwide',
            language VARCHAR(10) DEFAULT 'pl',

            -- Physical specs
            page_count INTEGER,
            trim_size VARCHAR(20),
            paper_type VARCHAR(20),

            -- Platform IDs
            kdp_book_id VARCHAR(100),
            draft2digital_id VARCHAR(100),
            smashwords_id VARCHAR(100),
            apple_books_id VARCHAR(100),
            kobo_id VARCHAR(100),
            google_play_id VARCHAR(100),
            empik_id VARCHAR(100),
            legimi_id VARCHAR(100),

            -- Timestamps
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP
        );
    END IF;
END$$;

-- Create indexes for publishing_metadata
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'publishing_metadata') THEN
        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_publishing_isbn') THEN
            CREATE INDEX idx_publishing_isbn ON publishing_metadata(isbn_13);
        END IF;
        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_publishing_project') THEN
            CREATE INDEX idx_publishing_project ON publishing_metadata(project_id);
        END IF;
    END IF;
END$$;

-- Create sales_tracking table
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'sales_tracking') THEN
        CREATE TABLE sales_tracking (
            id SERIAL PRIMARY KEY,
            publishing_metadata_id INTEGER NOT NULL REFERENCES publishing_metadata(id) ON DELETE CASCADE,

            -- Platform
            platform VARCHAR(50) NOT NULL,

            -- Time period
            period_start TIMESTAMP NOT NULL,
            period_end TIMESTAMP NOT NULL,

            -- Sales data
            units_sold INTEGER NOT NULL DEFAULT 0,
            units_returned INTEGER NOT NULL DEFAULT 0,
            pages_read INTEGER NOT NULL DEFAULT 0,

            -- Revenue
            gross_revenue DECIMAL(10,2) NOT NULL DEFAULT 0.0,
            royalty_earned DECIMAL(10,2) NOT NULL DEFAULT 0.0,
            currency VARCHAR(3) NOT NULL DEFAULT 'USD',

            -- Rankings
            best_rank INTEGER,
            average_rank INTEGER,
            category_rank INTEGER,

            -- Reviews
            new_reviews INTEGER NOT NULL DEFAULT 0,
            total_reviews INTEGER NOT NULL DEFAULT 0,
            average_rating DECIMAL(3,2),

            -- Synced
            synced_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    END IF;
END$$;

-- Create indexes for sales_tracking
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'sales_tracking') THEN
        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_sales_platform') THEN
            CREATE INDEX idx_sales_platform ON sales_tracking(platform);
        END IF;
        IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_sales_period') THEN
            CREATE INDEX idx_sales_period ON sales_tracking(period_start, period_end);
        END IF;
    END IF;
END$$;
