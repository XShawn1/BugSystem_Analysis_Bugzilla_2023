-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email VARCHAR(255),
    name VARCHAR(255),
    nick VARCHAR(255),
    real_name VARCHAR(255)
);

-- Reports (bugs/issues) table
-- CF columns are included in the custom fields table instead
CREATE TABLE reports (
    bug_id INTEGER PRIMARY KEY,
    alias TEXT,
    assigned_to TEXT,
    assigned_to_id INTEGER REFERENCES users(id),
    -- assigned_to_detail TEXT, -- Can be derived from assigned_to_id
    blocks INTEGER[],
    -- bugs TEXT, -- Changes History table
    cc text[],
    cc_id INTEGER[],
    -- cc_detail TEXT, -- Can be derived from cc_id
    classification TEXT,
    comment_count INTEGER,
    -- comments TEXT, -- Comments table
    component TEXT,
    creation_time TIMESTAMP,
    creator TEXT,
    creator_id INTEGER REFERENCES users(id),
    -- creator_detail TEXT, -- Can be derived from creator_id
    depends_on INTEGER[],
    dupe_of INTEGER,
    duplicates INTEGER[],
    -- flags TEXT[], -- Flags table
    groups TEXT[],
    is_cc_accessible BOOLEAN,
    is_confirmed BOOLEAN,
    is_creator_accessible BOOLEAN,
    is_open BOOLEAN,
    keywords TEXT[],
    last_change_time TIMESTAMP,
    mentors TEXT[],
    mentors_id INTEGER[],
    -- mentors_detail TEXT, -- Can be derived from mentors_id
    op_sys TEXT,
    platform TEXT,
    priority TEXT,
    product TEXT,
    qa_contact TEXT,
    qa_contact_id INTEGER REFERENCES users(id),
    -- qa_contact_detail TEXT,  -- Can be derived from qa_contact_id
    regressed_by TEXT[],
    regressions TEXT[],
    resolution TEXT,
    see_also TEXT[],
    severity TEXT,
    status TEXT,
    summary TEXT,
    target_milestone TEXT,
    type TEXT,
    update_token TEXT,
    url TEXT,
    version TEXT,
    votes INTEGER,
    whiteboard TEXT
);

-- Comments table
CREATE TABLE comments (
    id INTEGER PRIMARY KEY,
    bug_id INTEGER REFERENCES reports(bug_id),
    creator TEXT,
    creation_time TIMESTAMP,
    is_private BOOLEAN,
    time TIMESTAMP,
    author TEXT,
    raw_text TEXT,
    text TEXT,
    count INTEGER,
    tags TEXT[]
);

-- ChangesHistory table
CREATE TABLE changes_history (
    bug_id INTEGER REFERENCES reports(bug_id),
    "when" TIMESTAMP,
    who TEXT,
    field_name TEXT,
    removed TEXT,
    added TEXT
);

-- Flags table
CREATE TABLE flags (
    id INTEGER PRIMARY KEY,
    bug_id INTEGER REFERENCES reports(bug_id),
    type_id INTEGER,
    setter TEXT,
    name TEXT,
    status TEXT,
    creation_date TIMESTAMP,
    modification_date TIMESTAMP
);

-- Table for cf columns
CREATE TABLE custom_fields (
    bug_id INTEGER REFERENCES reports(bug_id),
    cf_field_name TEXT,
    value TEXT
);
