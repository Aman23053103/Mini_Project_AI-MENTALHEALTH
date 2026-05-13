-- ============================================================
-- SERENITY MINDSPACE — DATABASE SCHEMA v2.0
-- PostgreSQL 15+
-- Focus: Auth, User/Specialist profiles, Session booking,
--        Credential review by admin, Token economy
-- ============================================================

-- Enable UUID support
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================
-- USERS (base table for all account types)
-- ============================================================
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) UNIQUE NOT NULL,
    password_hash   VARCHAR(255),                   -- NULL for OAuth-only accounts
    full_name       VARCHAR(150) NOT NULL,
    user_type       VARCHAR(20) NOT NULL DEFAULT 'user'
                    CHECK (user_type IN ('user','specialist','admin')),
    is_verified     BOOLEAN NOT NULL DEFAULT FALSE,  -- email verified
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    avatar_url      VARCHAR(512),
    phone           VARCHAR(20),
    date_of_birth   DATE,
    preferred_lang  VARCHAR(10) DEFAULT 'en',
    timezone        VARCHAR(60) DEFAULT 'Asia/Kolkata',
    token_balance   INTEGER NOT NULL DEFAULT 0,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_login_at   TIMESTAMPTZ,
    deleted_at      TIMESTAMPTZ                     -- soft delete
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_type  ON users(user_type);

-- ============================================================
-- OAUTH PROVIDERS (Google Sign-In etc.)
-- ============================================================
CREATE TABLE oauth_accounts (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider    VARCHAR(30) NOT NULL,               -- 'google', 'apple'
    provider_id VARCHAR(255) NOT NULL,
    email       VARCHAR(255),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (provider, provider_id)
);

-- ============================================================
-- EMAIL VERIFICATION TOKENS
-- ============================================================
CREATE TABLE email_verifications (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token       VARCHAR(128) NOT NULL UNIQUE,
    expires_at  TIMESTAMPTZ NOT NULL,
    used_at     TIMESTAMPTZ
);

-- ============================================================
-- PASSWORD RESET TOKENS
-- ============================================================
CREATE TABLE password_resets (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token       VARCHAR(128) NOT NULL UNIQUE,
    expires_at  TIMESTAMPTZ NOT NULL,
    used_at     TIMESTAMPTZ
);

-- ============================================================
-- SPECIALIST PROFILES
-- ============================================================
CREATE TABLE specialist_profiles (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    bio                 TEXT,
    years_experience    SMALLINT NOT NULL DEFAULT 0,
    specializations     TEXT[] NOT NULL DEFAULT '{}',   -- e.g. {'Anxiety','CBT','Trauma'}
    languages           TEXT[] NOT NULL DEFAULT '{"English"}',
    approach            TEXT,                           -- therapy approach description
    session_price_chat  INTEGER NOT NULL DEFAULT 50,    -- tokens per 30min chat
    session_price_video INTEGER NOT NULL DEFAULT 100,   -- tokens per 30min video
    rating_avg          NUMERIC(3,2) DEFAULT 0,
    rating_count        INTEGER DEFAULT 0,
    is_available        BOOLEAN NOT NULL DEFAULT FALSE,
    next_available_at   TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ============================================================
-- SPECIALIST CREDENTIALS (documents for admin review)
-- ============================================================
CREATE TABLE specialist_credentials (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    specialist_id   UUID NOT NULL REFERENCES specialist_profiles(id) ON DELETE CASCADE,
    document_type   VARCHAR(30) NOT NULL
                    CHECK (document_type IN ('government_id','degree','practising_licence','other')),
    file_url        VARCHAR(512) NOT NULL,       -- secure storage URL (S3/Firebase)
    file_name       VARCHAR(255),
    mime_type       VARCHAR(80),
    upload_status   VARCHAR(20) NOT NULL DEFAULT 'uploaded'
                    CHECK (upload_status IN ('uploaded','under_review','approved','rejected')),
    -- Admin review fields
    reviewed_by     UUID REFERENCES users(id),   -- must be admin
    reviewed_at     TIMESTAMPTZ,
    review_notes    TEXT,                         -- admin's internal notes
    rejection_reason TEXT,                        -- shown to specialist if rejected
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_creds_specialist  ON specialist_credentials(specialist_id);
CREATE INDEX idx_creds_status      ON specialist_credentials(upload_status);
CREATE INDEX idx_creds_reviewer    ON specialist_credentials(reviewed_by);

-- ============================================================
-- SPECIALIST VERIFICATION STATUS (aggregate view)
-- ============================================================
CREATE TABLE specialist_verifications (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    specialist_id       UUID UNIQUE NOT NULL REFERENCES specialist_profiles(id) ON DELETE CASCADE,
    overall_status      VARCHAR(20) NOT NULL DEFAULT 'pending'
                        CHECK (overall_status IN ('pending','under_review','approved','rejected','suspended')),
    reviewed_by         UUID REFERENCES users(id),   -- admin who approved/rejected
    reviewed_at         TIMESTAMPTZ,
    admin_notes         TEXT,
    approved_at         TIMESTAMPTZ,
    suspended_reason    TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_verif_status ON specialist_verifications(overall_status);

-- ============================================================
-- WELLNESS ASSESSMENTS
-- ============================================================
CREATE TABLE assessments (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    feeling         VARCHAR(50),
    mood_score      SMALLINT CHECK (mood_score BETWEEN 1 AND 10),
    duration        VARCHAR(50),
    reasons         TEXT[],
    impact          VARCHAR(20),
    history         TEXT[],
    past_treatment  BOOLEAN DEFAULT FALSE,
    medications     TEXT,
    self_harm       VARCHAR(20),
    sleep_quality   VARCHAR(20),
    energy_level    VARCHAR(20),
    activities      VARCHAR(20),
    appetite        VARCHAR(20),
    support_system  VARCHAR(20),
    goals           TEXT[],
    support_style   VARCHAR(30),
    additional_notes TEXT,
    urgency_level   VARCHAR(10) CHECK (urgency_level IN ('low','medium','high','crisis')),
    completed_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_assessments_user ON assessments(user_id);

-- ============================================================
-- SESSIONS (bookings)
-- ============================================================
CREATE TABLE sessions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    specialist_id   UUID NOT NULL REFERENCES specialist_profiles(id),
    session_type    VARCHAR(10) NOT NULL CHECK (session_type IN ('chat','video')),
    status          VARCHAR(20) NOT NULL DEFAULT 'scheduled'
                    CHECK (status IN ('scheduled','active','completed','cancelled','no_show')),
    scheduled_at    TIMESTAMPTZ NOT NULL,
    started_at      TIMESTAMPTZ,
    ended_at        TIMESTAMPTZ,
    duration_mins   SMALLINT,
    tokens_charged  INTEGER NOT NULL DEFAULT 0,
    specialist_note TEXT,
    user_rating     SMALLINT CHECK (user_rating BETWEEN 1 AND 5),
    user_review     TEXT,
    rated_at        TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_sessions_user       ON sessions(user_id);
CREATE INDEX idx_sessions_specialist ON sessions(specialist_id);
CREATE INDEX idx_sessions_scheduled  ON sessions(scheduled_at);
CREATE INDEX idx_sessions_status     ON sessions(status);

-- ============================================================
-- CHAT MESSAGES (AI and specialist chat)
-- ============================================================
CREATE TABLE chat_messages (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id  UUID REFERENCES sessions(id) ON DELETE CASCADE,  -- NULL for AI chat
    user_id     UUID NOT NULL REFERENCES users(id),
    sender_type VARCHAR(15) NOT NULL CHECK (sender_type IN ('user','specialist','ai')),
    content     TEXT NOT NULL,
    is_flagged  BOOLEAN DEFAULT FALSE,   -- crisis/moderation flag
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_messages_session ON chat_messages(session_id);
CREATE INDEX idx_messages_user    ON chat_messages(user_id);

-- ============================================================
-- TOKEN TRANSACTIONS
-- ============================================================
CREATE TABLE token_transactions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id),
    amount          INTEGER NOT NULL,               -- positive = credit, negative = debit
    balance_after   INTEGER NOT NULL,
    transaction_type VARCHAR(30) NOT NULL
                    CHECK (transaction_type IN (
                        'welcome_bonus','purchase','ai_message',
                        'session_chat','session_video','session_refund',
                        'lucky_vault','admin_adjustment','expiry'
                    )),
    reference_id    UUID,                           -- session_id or payment_id
    payment_gateway VARCHAR(30),                    -- 'razorpay', 'stripe'
    gateway_order_id VARCHAR(255),
    gateway_payment_id VARCHAR(255),
    description     TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_tokens_user ON token_transactions(user_id);
CREATE INDEX idx_tokens_type ON token_transactions(transaction_type);

-- ============================================================
-- NOTIFICATIONS
-- ============================================================
CREATE TABLE notifications (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title       VARCHAR(200) NOT NULL,
    message     TEXT NOT NULL,
    notif_type  VARCHAR(30) DEFAULT 'info',
    is_read     BOOLEAN NOT NULL DEFAULT FALSE,
    action_url  VARCHAR(512),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_notif_user_unread ON notifications(user_id, is_read);

-- ============================================================
-- LUCKY VAULT SPINS (rate limiting)
-- ============================================================
CREATE TABLE vault_spins (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    spin_date   DATE NOT NULL DEFAULT CURRENT_DATE,
    won         BOOLEAN NOT NULL DEFAULT FALSE,
    tokens_won  INTEGER DEFAULT 0,
    UNIQUE (user_id, spin_date)
);

-- ============================================================
-- ADMIN AUDIT LOG (every admin action)
-- ============================================================
CREATE TABLE admin_audit_log (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    admin_id        UUID NOT NULL REFERENCES users(id),
    action          VARCHAR(80) NOT NULL,
    target_type     VARCHAR(40),                    -- 'specialist_credential', 'user', etc.
    target_id       UUID,
    old_value       JSONB,
    new_value       JSONB,
    ip_address      INET,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_admin  ON admin_audit_log(admin_id);
CREATE INDEX idx_audit_target ON admin_audit_log(target_type, target_id);

-- ============================================================
-- SPECIALIST AVAILABILITY SLOTS
-- ============================================================
CREATE TABLE availability_slots (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    specialist_id   UUID NOT NULL REFERENCES specialist_profiles(id) ON DELETE CASCADE,
    slot_start      TIMESTAMPTZ NOT NULL,
    slot_end        TIMESTAMPTZ NOT NULL,
    is_booked       BOOLEAN NOT NULL DEFAULT FALSE,
    session_id      UUID REFERENCES sessions(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_slots_specialist ON availability_slots(specialist_id);
CREATE INDEX idx_slots_start      ON availability_slots(slot_start);

-- ============================================================
-- TRIGGERS — auto-update updated_at
-- ============================================================
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated          BEFORE UPDATE ON users                   FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_specialist_updated     BEFORE UPDATE ON specialist_profiles      FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_verif_updated          BEFORE UPDATE ON specialist_verifications FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_sessions_updated       BEFORE UPDATE ON sessions                 FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ============================================================
-- VIEWS
-- ============================================================

-- Specialists pending admin review
CREATE VIEW v_pending_credential_reviews AS
SELECT
    sc.id             AS credential_id,
    sc.document_type,
    sc.file_url,
    sc.upload_status,
    sc.created_at     AS submitted_at,
    u.full_name       AS specialist_name,
    u.email           AS specialist_email,
    sv.overall_status AS verification_status
FROM specialist_credentials sc
JOIN specialist_profiles sp ON sc.specialist_id = sp.id
JOIN users u                ON sp.user_id = u.id
JOIN specialist_verifications sv ON sv.specialist_id = sp.id
WHERE sc.upload_status IN ('uploaded','under_review')
ORDER BY sc.created_at ASC;

-- Approved specialists (public directory)
CREATE VIEW v_approved_specialists AS
SELECT
    sp.id, u.full_name, u.avatar_url,
    sp.bio, sp.years_experience, sp.specializations,
    sp.languages, sp.rating_avg, sp.rating_count,
    sp.session_price_chat, sp.session_price_video,
    sp.is_available, sp.next_available_at
FROM specialist_profiles sp
JOIN users u ON sp.user_id = u.id
JOIN specialist_verifications sv ON sv.specialist_id = sp.id
WHERE sv.overall_status = 'approved'
  AND u.is_active = TRUE
  AND u.deleted_at IS NULL;

-- ============================================================
-- INITIAL ADMIN SEED (change password before production!)
-- ============================================================
INSERT INTO users (email, password_hash, full_name, user_type, is_verified)
VALUES (
    'admin@serenitymindspace.com',
    crypt('ChangeMe123!', gen_salt('bf', 12)),
    'Serenity Admin',
    'admin',
    TRUE
);
