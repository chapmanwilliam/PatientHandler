SELECT
    ROWID,
    SecondName || ', ' || FirstName || ' (' ||
    strftime('%d-%m-%Y',DOB) || ')'
FROM PATIENTS
ORDER BY SecondName