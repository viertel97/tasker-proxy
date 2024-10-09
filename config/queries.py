ght_get_old_answers_query = """
SELECT 
    LatestGHT.id AS ght_id,
    LatestGHT.code AS ght_code,
    LatestGHT.value,
    LatestGHT.ts,
    LatestGHT.offset,
    LatestGHT.created_at,
    LatestGHT.multiplier AS ght_multiplier,
    COALESCE(gqd_e.id, gqd_m.id, gqm.id, gqq.id, gqw.id, gqy.id) AS id,
    COALESCE(gqd_e.message, gqd_m.message, gqm.message, gqq.message, gqw.message, gqy.message) AS message
FROM 
    (
        SELECT
            g.id,
            g.code,
            g.value,
            g.ts,
            g.offset,
            g.created_at,
            g.multiplier
        FROM
            ght g
        INNER JOIN (
            SELECT
                code,
                MAX(ts) AS max_ts
            FROM
                ght
            GROUP BY
                code
        ) AS latest ON g.code = latest.code AND g.ts = latest.max_ts
    ) AS LatestGHT
LEFT JOIN 
    ght_questions_daily_evening gqd_e ON LatestGHT.code = gqd_e.code
LEFT JOIN 
    ght_questions_daily_morning gqd_m ON LatestGHT.code = gqd_m.code
LEFT JOIN 
    ght_questions_monthly gqm ON LatestGHT.code = gqm.code
LEFT JOIN 
    ght_questions_quarterly gqq ON LatestGHT.code = gqq.code
LEFT JOIN 
    ght_questions_weekly gqw ON LatestGHT.code = gqw.code
LEFT JOIN 
    ght_questions_yearly gqy ON LatestGHT.code = gqy.code;
"""

activity_query = """
SELECT
    a.*,
    GROUP_CONCAT(
        CASE
            WHEN c.last_name IS NULL OR c.last_name = '' THEN c.first_name
            ELSE CONCAT(c.first_name, ' ', c.last_name)
        END SEPARATOR '~'
    ) AS people,
    CONCAT(
        DATE_FORMAT(a.happened_at, '%Y-%m-%d'),
        '-',
        a.summary)
    AS filename,
    GROUP_CONCAT(
        DISTINCT e.name SEPARATOR '~'
    ) AS emotions
FROM
    activities AS a
    LEFT JOIN activity_contact AS ac ON a.id = ac.activity_id
    LEFT JOIN contacts AS c ON ac.contact_id = c.id
    LEFT JOIN emotion_activity AS ea ON a.id = ea.activity_id
    LEFT JOIN emotions AS e ON ea.emotion_id = e.id
WHERE
    a.summary != 'TBD' and a.happened_at = '{happened_at}'
GROUP BY
    a.id
ORDER BY
    a.happened_at;
                    """