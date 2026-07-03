SELECT 
    ps.player_id,
    p.player_name,
    ROUND(AVG(ps.kills), 2) AS avg_kills
FROM player_stats ps
JOIN players p
ON ps.player_id = p.player_id
GROUP BY ps.player_id, p.player_name
ORDER BY avg_kills DESC