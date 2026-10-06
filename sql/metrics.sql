-- Share of Voice
WITH mentions AS (
  SELECT candidate_id, COUNT(*) AS mentions
  FROM post_candidates
  GROUP BY candidate_id
)
SELECT candidate_id, mentions,
       ROUND(100.0 * mentions / SUM(mentions) OVER (), 2) AS share_of_voice_pct
FROM mentions
ORDER BY mentions DESC;

-- Volume diário
SELECT DATE(p.published_at) AS day, pc.candidate_id, COUNT(*) AS mentions
FROM post_candidates pc
JOIN raw_posts p ON p.post_id = pc.post_id
GROUP BY DATE(p.published_at), pc.candidate_id
ORDER BY day, mentions DESC;

-- Engajamento bruto
SELECT pc.candidate_id,
       SUM(p.likes + p.comments + p.shares + p.views) AS engagement_raw
FROM post_candidates pc
JOIN raw_posts p ON p.post_id = pc.post_id
GROUP BY pc.candidate_id
ORDER BY engagement_raw DESC;

-- Sentimento
SELECT pc.candidate_id, a.sentiment, COUNT(*) AS posts
FROM post_candidates pc
JOIN ai_classification a ON a.post_id = pc.post_id
GROUP BY pc.candidate_id, a.sentiment;

-- Temas
SELECT pc.candidate_id, a.topic, COUNT(*) AS posts
FROM post_candidates pc
JOIN ai_classification a ON a.post_id = pc.post_id
GROUP BY pc.candidate_id, a.topic
ORDER BY pc.candidate_id, posts DESC;
