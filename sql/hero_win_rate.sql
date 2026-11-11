SELECT 
    ps.hero_id,
    h.hero_name,
    ROUND(SUM(ps.win) * 100 / COUNT(*),2) AS win_rate,
    SUM(ps.win) AS win_counts,
    COUNT(*) AS appearances
FROM player_stats ps
JOIN heroes h 
ON ps.hero_id = h.hero_id
GROUP BY ps.hero_id
ORDER BY win_rate DESC;