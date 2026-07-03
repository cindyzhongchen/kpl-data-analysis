SELECT 
    ps.hero_id,
    h.hero_name,
    ROUND(ps.win * 100 / COUNT(*),1) AS win_rate
FROM player_stats ps
JOIN heroes h 
ON ps.hero_id = h.hero_id
GROUP BY ps.hero_id
ORDER BY win_rate DESC;