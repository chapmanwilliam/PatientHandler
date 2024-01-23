SELECT
    PATIENTS.Title || ' ' || Patients.SecondName as Name,
    PATIENTS.FirstName || ' ' || PATIENTS.SecondName as FullName,
    strftime('%d-%m-%Y',Patients.DOB) as DOB,
    PATIENTS.NHS_NO
FROM Patients
WHERE PATIENTS.ROWID=?