SELECT 
    side,
    ROUND(100.0 * SUM(win) / COUNT(*), 2) AS win_rate
FROM player_stats
GROUP BY side;
