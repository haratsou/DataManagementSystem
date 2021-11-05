The database will store records of students, 
tutors, courses and grades in a university.

The project will include the following tables:
- user (user ID, username, email, password, user role, forename, last name, date of birth,
  email, salary, subjects (fk), grades (fk) )
- subjects (ID, name, semester offered, teachers (fk), students (fk))
- grades (grade, subject (fk), student(fk))

User roles will determine the information that a user can access. Each student is able to
access their own subjects and grades only and likewise each tutor. Admin users can access and
modify all the information. 

