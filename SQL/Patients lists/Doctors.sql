SELECT
    ROWID as ID,
    DOCTORS.Title || ' ' || DOCTORS.First_Name || ' ' || Doctors.Second_Name || ' (' || DOCTORS.Job_Title || ') ' as TXT,
    USE as USE
FROM DOCTORS
ORDER BY SecondName