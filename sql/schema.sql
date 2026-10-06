CREATE TABLE raw_posts (
    post_id TEXT PRIMARY KEY,
    platform TEXT NOT NULL,
    author_id TEXT,
    author_name TEXT,
    published_at TIMESTAMP NOT NULL,
    text TEXT NOT NULL,
    url TEXT,
    language TEXT,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    views INTEGER DEFAULT 0,
    collected_at TIMESTAMP NOT NULL,
    raw_json TEXT
);

CREATE TABLE post_candidates (
    post_id TEXT NOT NULL,
    candidate_id TEXT NOT NULL,
    detection_method TEXT,
    confidence NUMERIC,
    PRIMARY KEY (post_id, candidate_id)
);

CREATE TABLE ai_classification (
    post_id TEXT PRIMARY KEY,
    topic TEXT,
    sentiment TEXT,
    stance TEXT,
    narrative TEXT,
    is_sarcasm BOOLEAN,
    is_news_report BOOLEAN,
    is_campaign_content BOOLEAN,
    confidence NUMERIC,
    model TEXT,
    classified_at TIMESTAMP
);

CREATE TABLE events (
    event_id TEXT PRIMARY KEY,
    event_name TEXT,
    event_type TEXT,
    start_at TIMESTAMP,
    end_at TIMESTAMP,
    description TEXT
);

CREATE INDEX idx_raw_platform_time ON raw_posts(platform, published_at);
CREATE INDEX idx_pc_candidate ON post_candidates(candidate_id);
CREATE INDEX idx_ai_topic ON ai_classification(topic);
