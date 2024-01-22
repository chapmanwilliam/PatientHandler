SELECT
    TEL_NOS.ROWID,
    TEL_NOS.TEL_NO,
    TEL_NOS.Use
FROM PATIENTS
JOIN TEL_NOS ON TEL_NOS.PATIENT_ID=PATIENTS.ROWID
WHERE PATIENTS.ROWID = ? AND TEL_NOS.USE=1
ORDER BY Use DESC