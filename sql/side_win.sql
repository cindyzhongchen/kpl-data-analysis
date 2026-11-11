SELECT 
    side,
    ROUND(100.0 * SUM(win) / COUNT(*), 2) AS win_rate,
    SUM(win) AS total_wins
FROM player_stats
GROUP BY side;
