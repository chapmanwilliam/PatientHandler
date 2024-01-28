SELECT
    ROWID as ID,
    Second_Name || ', ' || First_Name || ' (' ||
    strftime('%d-%m-%Y',DOB) || ')' as TXT,
    USE as USE
FROM PATIENTS
ORDER BY SecondName