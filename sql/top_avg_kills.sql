SELECT 
    ps.player_id,
    p.player_name, 
    AVG(ps.kills) AS avg_kills
FROM player_stats ps
JOIN players p ON ps.player_id = p.player_id
GROUP BY ps.player_id
ORDER BY avg_kills DESC;

