SELECT
    ROWID,
    SecondName || ', ' || FirstName || ' (' ||
    strftime('%d-%m-%Y',DOB) || ')' as PatientInfo
FROM PATIENTS
WHERE PatientInfo LIKE "%" || ? || "%"
ORDER BY SecondName