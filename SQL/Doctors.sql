SELECT
DOCTORS.ROWID,
Patients.Title || ' ' || Patients.FirstName || ' ' || Patients.SecondName as Patient,
DOCTORS.Title || ' ' || DOCTORS.FirstName || ' ' || Doctors.SecondName as Doctor,
DOCTORS.Job_Title,
REFERRING_DOCTORS.USE
FROM Patients
JOIN REFERRING_DOCTORS ON Patients.ROWID=REFERRING_DOCTORS.PATIENT_ID
JOIN DOCTORS ON REFERRING_DOCTORS.DOCTOR_ID=DOCTORS.ROWID
WHERE Patients.ROWID=?