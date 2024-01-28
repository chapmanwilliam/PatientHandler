SELECT
    PATIENTS.Title || ' ' || Patients.Second_Name as Name,
    PATIENTS.First_Name || ' ' || PATIENTS.Second_Name as FullName,
    strftime('%d-%m-%Y',Patients.Date_of_birth) as DOB,
    PATIENTS.NHS_no
FROM Patients
WHERE PATIENTS.ROWID=?