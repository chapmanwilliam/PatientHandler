SELECT
    ROWID as ID,
    Second_Name || ', ' || First_Name || ' (' ||
    strftime('%d-%m-%Y',Date_of_birth) || ')' as TXT,
    USE as USE
FROM PATIENTS
WHERE TXT LIKE "%" || ? || "%"
ORDER BY Second_Name