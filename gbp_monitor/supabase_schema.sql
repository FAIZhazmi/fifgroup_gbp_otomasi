-- ============================================================================
-- SUPABASE SCHEMA untuk GBP Monitor
-- ============================================================================
-- File ini berisi schema database untuk Supabase PostgreSQL.
-- Copy & paste ke Supabase SQL Editor untuk membuat semua tabel.
--
-- Cara menggunakan:
-- 1. Buka Supabase Dashboard
-- 2. Pergi ke SQL Editor
-- 3. Copy semua query di file ini
-- 4. Execute
-- ============================================================================

-- ────────────────────────────────────────────────────────────────────────────
-- 1. GBP Fetch Run (Master Table)
-- ────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS gbp_fetch_run (
    id BIGSERIAL PRIMARY KEY,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMPTZ,
    total_records INT DEFAULT 0,
    status VARCHAR(50) DEFAULT 'completed',
    source VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index untuk performa
CREATE INDEX IF NOT EXISTS idx_fetch_run_started_at ON gbp_fetch_run(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_fetch_run_status ON gbp_fetch_run(status);

COMMENT ON TABLE gbp_fetch_run IS 'Master table untuk tracking setiap fetch run dari GBP API';


-- ────────────────────────────────────────────────────────────────────────────
-- 2. GBP Location Snapshot
-- ────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS gbp_location_snapshot (
    id BIGSERIAL PRIMARY KEY,
    run_id BIGINT NOT NULL REFERENCES gbp_fetch_run(id) ON DELETE CASCADE,
    
    -- Identifiers
    store_code VARCHAR(255),
    business_name VARCHAR(500),
    location_name VARCHAR(500),
    
    -- Status & Verifikasi
    status VARCHAR(100),
    verification_status VARCHAR(100),
    
    -- Address & Location
    address TEXT,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    coord_status VARCHAR(50),
    
    -- Area & Network
    area VARCHAR(255),
    network VARCHAR(255),
    network_type VARCHAR(100),
    
    -- Metadata
    phone_number VARCHAR(50),
    website_url VARCHAR(500),
    google_maps_url VARCHAR(500),
    place_id VARCHAR(255),
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes untuk performa query
CREATE INDEX IF NOT EXISTS idx_snapshot_run_id ON gbp_location_snapshot(run_id);
CREATE INDEX IF NOT EXISTS idx_snapshot_store_code ON gbp_location_snapshot(store_code);
CREATE INDEX IF NOT EXISTS idx_snapshot_business_name ON gbp_location_snapshot(business_name);
CREATE INDEX IF NOT EXISTS idx_snapshot_status ON gbp_location_snapshot(status);
CREATE INDEX IF NOT EXISTS idx_snapshot_area ON gbp_location_snapshot(area);
CREATE INDEX IF NOT EXISTS idx_snapshot_network ON gbp_location_snapshot(network);
CREATE INDEX IF NOT EXISTS idx_snapshot_created_at ON gbp_location_snapshot(created_at DESC);

-- Composite index untuk query filtering
CREATE INDEX IF NOT EXISTS idx_snapshot_run_status ON gbp_location_snapshot(run_id, status);

COMMENT ON TABLE gbp_location_snapshot IS 'Snapshot lokasi GBP pada setiap fetch run';


-- ────────────────────────────────────────────────────────────────────────────
-- 3. GBP Master Location (Master Data Reference)
-- ────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS gbp_master_location (
    id BIGSERIAL PRIMARY KEY,
    
    -- Identifiers
    store_code VARCHAR(255) UNIQUE NOT NULL,
    network_name VARCHAR(500),
    business_name VARCHAR(500),
    
    -- Status
    current_status VARCHAR(100),
    
    -- Location
    address TEXT,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    
    -- Metadata
    area VARCHAR(255),
    network VARCHAR(255),
    network_type VARCHAR(100),
    
    -- Tracking
    last_updated TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_master_store_code ON gbp_master_location(store_code);
CREATE INDEX IF NOT EXISTS idx_master_network_name ON gbp_master_location(network_name);
CREATE INDEX IF NOT EXISTS idx_master_status ON gbp_master_location(current_status);
CREATE INDEX IF NOT EXISTS idx_master_area ON gbp_master_location(area);

COMMENT ON TABLE gbp_master_location IS 'Master data lokasi (reference untuk reconciliation)';


-- ────────────────────────────────────────────────────────────────────────────
-- 4. GBP Reconciliation Job
-- ────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS gbp_reconciliation_job (
    id BIGSERIAL PRIMARY KEY,
    
    -- Job info
    source_type VARCHAR(50),
    source_label VARCHAR(500),
    
    -- Stats
    total_master INT DEFAULT 0,
    total_api INT DEFAULT 0,
    total_matched INT DEFAULT 0,
    total_updated INT DEFAULT 0,
    total_unmatched INT DEFAULT 0,
    
    -- Summary (JSONB untuk flexible data)
    summary JSONB,
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_recon_job_created_at ON gbp_reconciliation_job(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_recon_job_source_type ON gbp_reconciliation_job(source_type);

COMMENT ON TABLE gbp_reconciliation_job IS 'Job rekonsiliasi status verifikasi GBP';


-- ────────────────────────────────────────────────────────────────────────────
-- 5. GBP Reconciliation Result
-- ────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS gbp_reconciliation_result (
    id BIGSERIAL PRIMARY KEY,
    job_id BIGINT NOT NULL REFERENCES gbp_reconciliation_job(id) ON DELETE CASCADE,
    
    -- Identifiers
    store_code VARCHAR(255),
    network_name VARCHAR(500),
    business_name VARCHAR(500),
    location_name VARCHAR(500),
    identifier_value VARCHAR(500),
    
    -- Matching
    match_status VARCHAR(50),
    match_rule VARCHAR(100),
    
    -- Status change
    old_status VARCHAR(100),
    new_status VARCHAR(100),
    status_changed BOOLEAN DEFAULT FALSE,
    
    -- Process
    process_status VARCHAR(50),
    change_note TEXT,
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_recon_result_job_id ON gbp_reconciliation_result(job_id);
CREATE INDEX IF NOT EXISTS idx_recon_result_store_code ON gbp_reconciliation_result(store_code);
CREATE INDEX IF NOT EXISTS idx_recon_result_match_status ON gbp_reconciliation_result(match_status);
CREATE INDEX IF NOT EXISTS idx_recon_result_status_changed ON gbp_reconciliation_result(status_changed);

COMMENT ON TABLE gbp_reconciliation_result IS 'Detail hasil rekonsiliasi per location';


-- ────────────────────────────────────────────────────────────────────────────
-- 6. GBP Master Data History (Audit Trail)
-- ────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS gbp_master_data_history (
    id BIGSERIAL PRIMARY KEY,
    store_code VARCHAR(255),
    
    -- Change tracking
    field_name VARCHAR(100),
    old_value TEXT,
    new_value TEXT,
    
    -- Context
    changed_by VARCHAR(255),
    change_source VARCHAR(100),
    notes TEXT,
    
    -- Timestamps
    changed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_history_store_code ON gbp_master_data_history(store_code);
CREATE INDEX IF NOT EXISTS idx_history_changed_at ON gbp_master_data_history(changed_at DESC);

COMMENT ON TABLE gbp_master_data_history IS 'Audit trail untuk perubahan master data';


-- ────────────────────────────────────────────────────────────────────────────
-- Triggers untuk auto-update updated_at
-- ────────────────────────────────────────────────────────────────────────────

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger ke semua tabel yang punya updated_at
CREATE TRIGGER update_gbp_fetch_run_updated_at
    BEFORE UPDATE ON gbp_fetch_run
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_gbp_location_snapshot_updated_at
    BEFORE UPDATE ON gbp_location_snapshot
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_gbp_master_location_updated_at
    BEFORE UPDATE ON gbp_master_location
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_gbp_reconciliation_job_updated_at
    BEFORE UPDATE ON gbp_reconciliation_job
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- ────────────────────────────────────────────────────────────────────────────
-- Views untuk reporting (Optional)
-- ────────────────────────────────────────────────────────────────────────────

-- View: Latest snapshot per location
CREATE OR REPLACE VIEW v_latest_location_status AS
SELECT DISTINCT ON (store_code)
    id,
    run_id,
    store_code,
    business_name,
    location_name,
    status,
    verification_status,
    address,
    latitude,
    longitude,
    area,
    network,
    network_type,
    created_at
FROM gbp_location_snapshot
ORDER BY store_code, created_at DESC;

COMMENT ON VIEW v_latest_location_status IS 'Latest status untuk setiap location';


-- View: Verification summary by area
CREATE OR REPLACE VIEW v_verification_by_area AS
SELECT
    area,
    COUNT(*) as total_locations,
    COUNT(*) FILTER (WHERE status = 'Verified') as verified,
    COUNT(*) FILTER (WHERE status = 'Need Verification') as need_verification,
    COUNT(*) FILTER (WHERE status = 'Suspended') as suspended,
    COUNT(*) FILTER (WHERE status = 'Duplicate') as duplicate,
    ROUND(
        COUNT(*) FILTER (WHERE status = 'Verified')::DECIMAL / 
        NULLIF(COUNT(*), 0) * 100, 
        2
    ) as verification_rate
FROM v_latest_location_status
WHERE area IS NOT NULL
GROUP BY area
ORDER BY verification_rate DESC;

COMMENT ON VIEW v_verification_by_area IS 'Summary verifikasi per area';


-- ────────────────────────────────────────────────────────────────────────────
-- Row Level Security (RLS) - Opsional untuk production
-- ────────────────────────────────────────────────────────────────────────────

-- Uncomment jika ingin aktifkan RLS
/*
ALTER TABLE gbp_fetch_run ENABLE ROW LEVEL SECURITY;
ALTER TABLE gbp_location_snapshot ENABLE ROW LEVEL SECURITY;
ALTER TABLE gbp_master_location ENABLE ROW LEVEL SECURITY;
ALTER TABLE gbp_reconciliation_job ENABLE ROW LEVEL SECURITY;
ALTER TABLE gbp_reconciliation_result ENABLE ROW LEVEL SECURITY;

-- Policy: Allow read for authenticated users
CREATE POLICY "Allow read for authenticated users" ON gbp_fetch_run
    FOR SELECT
    TO authenticated
    USING (true);

-- Tambahkan policies lainnya sesuai kebutuhan
*/


-- ============================================================================
-- END OF SCHEMA
-- ============================================================================

-- Verify tables created
SELECT 
    schemaname, 
    tablename, 
    tableowner 
FROM pg_tables 
WHERE tablename LIKE 'gbp_%' 
ORDER BY tablename;

