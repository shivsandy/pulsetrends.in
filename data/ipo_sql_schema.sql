-- PulseTrends IPO Intelligence Database SQL Schema
-- Generated: 2026-06-17 12:56:31 UTC
-- Database: PostgreSQL / MySQL compatible

CREATE TABLE IF NOT EXISTS ipos (
    id SERIAL PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    ticker VARCHAR(20),
    exchange VARCHAR(50),
    sector VARCHAR(100),
    industry VARCHAR(100),
    status VARCHAR(20) DEFAULT 'listed',
    ipo_date DATE,
    issue_price DECIMAL(12,2),
    price_band_low DECIMAL(12,2),
    price_band_high DECIMAL(12,2),
    listing_price DECIMAL(12,2),
    current_price DECIMAL(12,2),
    offer_size VARCHAR(50),
    market_cap_at_ipo DECIMAL(18,2),
    current_market_cap DECIMAL(18,2),
    gmp DECIMAL(12,2),
    subscription VARCHAR(20),

    -- AI Scores
    ai_score DECIMAL(5,1),
    ai_rating VARCHAR(50),
    ai_confidence VARCHAR(10),
    fundamentals_score DECIMAL(5,1),
    ipo_demand_score DECIMAL(5,1),
    valuation_score DECIMAL(5,1),
    governance_score DECIMAL(5,1),
    business_quality_score DECIMAL(5,1),
    post_listing_score DECIMAL(5,1),

    -- Source
    source VARCHAR(50),
    country VARCHAR(10),

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_ipos_company_name ON ipos(company_name);
CREATE INDEX idx_ipos_ticker ON ipos(ticker);
CREATE INDEX idx_ipos_exchange ON ipos(exchange);
CREATE INDEX idx_ipos_sector ON ipos(sector);
CREATE INDEX idx_ipos_status ON ipos(status);
CREATE INDEX idx_ipos_ai_score ON ipos(ai_score DESC);
CREATE INDEX idx_ipos_country ON ipos(country);
CREATE INDEX idx_ipos_ipo_date ON ipos(ipo_date);

-- IPO Scores Archive Table
CREATE TABLE IF NOT EXISTS ipo_scores_archive (
    id SERIAL PRIMARY KEY,
    ipo_id INTEGER REFERENCES ipos(id),
    ai_score DECIMAL(5,1),
    fundamentals_score DECIMAL(5,1),
    ipo_demand_score DECIMAL(5,1),
    valuation_score DECIMAL(5,1),
    governance_score DECIMAL(5,1),
    business_quality_score DECIMAL(5,1),
    post_listing_score DECIMAL(5,1),
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- IPO Red Flags Table
CREATE TABLE IF NOT EXISTS ipo_red_flags (
    id SERIAL PRIMARY KEY,
    ipo_id INTEGER REFERENCES ipos(id),
    flag TEXT NOT NULL,
    severity VARCHAR(10) DEFAULT 'medium',
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- IPO Risk Factors Table
CREATE TABLE IF NOT EXISTS ipo_risk_factors (
    id SERIAL PRIMARY KEY,
    ipo_id INTEGER REFERENCES ipos(id),
    risk TEXT NOT NULL,
    category VARCHAR(50),
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- IPO Sources Tracking
CREATE TABLE IF NOT EXISTS ipo_sources (
    id SERIAL PRIMARY KEY,
    ipo_id INTEGER REFERENCES ipos(id),
    source_name VARCHAR(100) NOT NULL,
    source_url TEXT,
    last_validated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- View: Top Rated IPOs
CREATE OR REPLACE VIEW top_rated_ipos AS
SELECT company_name, ticker, exchange, sector, ai_score, ai_rating
FROM ipos
WHERE ai_score >= 80
ORDER BY ai_score DESC;

-- View: Sector Performance Summary
CREATE OR REPLACE VIEW sector_performance AS
SELECT
    sector,
    COUNT(*) as ipo_count,
    ROUND(AVG(ai_score), 1) as avg_score,
    MAX(ai_score) as max_score,
    MIN(ai_score) as min_score
FROM ipos
WHERE sector IS NOT NULL AND sector != ''
GROUP BY sector
ORDER BY avg_score DESC;

-- View: Exchange Distribution
CREATE OR REPLACE VIEW exchange_summary AS
SELECT
    exchange,
    COUNT(*) as ipo_count,
    ROUND(AVG(ai_score), 1) as avg_score
FROM ipos
WHERE exchange IS NOT NULL AND exchange != ''
GROUP BY exchange
ORDER BY ipo_count DESC;
