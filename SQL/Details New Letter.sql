SELECT
    PATIENTS.Title || ' ' || Patients.SecondName as Name,
    ADDRESSES.address || ' ' || ADDRESSES.POST_CODE || ', ' || ADDRESSES.COUNTRY as Address,
    PATIENTS.FirstName || ' ' || PATIENTS.SecondName as FullName,
    strftime('%d-%m-%Y',Patients.DOB) as DOB,
    PATIENTS.NHS_NO
FROM Patients
JOIN ADDRESSES ON PATIENTS.ROWID = ADDRESSES.PATIENT_ID
WHERE PATIENTS.ROWID=? AND ADDRESSES.Use=1