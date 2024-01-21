SELECT Patients.Title || ' ' || Patients.FirstName || ' ' || Patients.SecondName as Patient,
DOCTORS.Title || ' ' || DOCTORS.FirstName || ' ' || Doctors.SecondName as Doctor
FROM Patients
JOIN REFERRRING_DOCTORS ON Patients.ROWID=REFERRRING_DOCTORS.PATIENT_ID
JOIN DOCTORS ON REFERRRING_DOCTORS.DOCTOR_ID=DOCTORS.ROWID
WHERE Patients.ROWID=1