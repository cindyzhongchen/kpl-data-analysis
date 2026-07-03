SELECT 
    p.player_id,
    p.player_name,
    (ps.kills + ps.assists) * 1.0 / CASE 
        WHEN ps.deaths = 0 THEN 1
        ELSE ps.deaths
    END AS kda
FROM player_stats ps
JOIN players p ON ps.player_id = p.player_id
ORDER BY kda DESC;