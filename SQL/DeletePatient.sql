DELETE
FROM Patients
WHERE ROWID=?;

DELETE
FROM EMAILS
WHERE PATIENT_ID=?;

DELETE
FROM ADDRESSES
WHERE PATIENT_ID=?;

DELETE
FROM REFERRING_DOCTORS
WHERE PATIENT_ID=?;

DELETE
FROM TEL_NOS
WHERE PATIENT_ID=?