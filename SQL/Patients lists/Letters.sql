SELECT
    ROWID as ID,
    Title as TXT,
    Final as USE
FROM CORRESPONDENCE
WHERE TXT LIKE "%" || ? || "%"
ORDER BY Date DESC
