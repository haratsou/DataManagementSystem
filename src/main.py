import sqlite3
import csv

# Define DBOperation class to manage all data into the database.
# Give a name of your choice to the database

class DBOperations:
    sql_create_table = "CREATE TABLE EmployeeUoB (employeeID INTEGER PRIMARY KEY AUTOINCREMENT, title VARCHAR(20) NOT " \
                       "NULL, forename VARCHAR(20) NOT NULL, surname VARCHAR(20) NOT NULL, email VARCHAR(50) NOT " \
                       "NULL, salary FLOAT UNSIGNED NOT NULL) "

    attributes = ["Employee ID:", "Title:", "Forename:", "Surname:", "Email:", "Salary:"]

    sql_insert = "INSERT INTO EmployeeUoB (title, forename, surname, email, salary) VALUES (?,?,?,?,?)"

    sql_bulk_insert = "BULK INSERT EmployeeUoB FROM %s WITH (FORMAT = 'CSV', FIRSTROW = 2)"

    sql_select_all = "SELECT * FROM EmployeeUoB ORDER BY %s"
    sql_search = "SELECT * FROM EmployeeUoB WHERE %s = ?"
    sql_update_data = "UPDATE EmployeeUoB SET %s = ? WHERE employeeID = ?"
    sql_delete_data = "DELETE FROM EmployeeUoB WHERE employeeID = ?"
    sql_drop_table = "DROP TABLE EmployeeUob"

    def __init__(self):
        self.get_connection()

    def _get_employee_id(self):
        """Get the employee id from the user"""

        employeeID = 0

        while True:
            try:
                employeeID = int(input("Enter Employee ID: "))
                break
            except ValueError:
                print("\nPlease enter a valid employee ID. To return to the main menu press 0.")
                continue

        if employeeID == 0:
            raise ValueError()

        return employeeID

    def _get_user_choice(self, options, functionality):
        """Get the option from the user"""

        userChoice = 0
        while True:
            print(" Options:")
            print("**********")

            for i, option in enumerate(options):
                print(str(i + 1) + ". " + functionality + " " + option)

            print(str(len(options) + 1) + ". Return to the main menu")

            try:
                # subtract 1 from user choice, as menu starts from 1 while list index starts from 0
                userChoice = int(input("\nChoose a number from the menu above: ")) - 1
                print()
            except ValueError:
                print("\nPlease enter a number from the options above.\n")
                continue

            if userChoice < 0 or userChoice > len(options):
                # user choice out of range of the valid options
                print("\nPlease enter a number from the options above.\n")
                continue
            elif userChoice == len(options):
                # returns user to the main menu
                raise ValueError()
            else:
                break

        return userChoice

    def get_connection(self):
        """Establish a connection with the database"""

        self.conn = sqlite3.connect("DBName.db")
        self.cur = self.conn.cursor()

    def create_table(self):
        """Create a new database table"""

        self.cur.execute(self.sql_create_table)
        self.conn.commit()
        print("Table created successfully")

    def insert_data(self):
        """Insert a new employee to the database"""

        emp = Employee()
        emp.set_title(input("Enter Employee Title: "))
        emp.set_forename(input("Enter Employee Forename: "))
        emp.set_surname(input("Enter Employee Surname: "))
        emp.set_email(input("Enter Employee Email: "))
        emp.set_salary(float(input("Enter Employee Salary: ")))

        if emp.salary < 0:
            raise ValueError("Salary cannot be negative. Please try again.")

        self.cur.execute(self.sql_insert, tuple(str(emp).split("\n")))

        self.conn.commit()
        print("\nInserted data successfully")

    def import_from_csv(self):
        """Bulk import employee data from CSV file"""

        csvFile = input("Enter CSV file name: ")
        csvList = []

        with open(csvFile) as f:
            for line in csv.reader(f):
                line[4] = float(line[4])
                csvList.append(tuple(line))

        result = self.cur.executemany(self.sql_insert, csvList)
        self.conn.commit()

        if result.rowcount != 0:
            print(str(result.rowcount) + " row(s) imported.")

    def export_to_csv(self):
        """Export all employee data into a CSV file that the user names"""

        csvFile = input("Select new CSV file name: ")
        self.cur.execute(self.sql_select_all % "employeeID")

        with open(csvFile, "w", newline='') as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow([i[0] for i in self.cur.description])
            csv_writer.writerows(self.cur)
        print("CVS exported successfully.")

    def select_all(self):
        """Display all the employee data ordered by the field the user chooses"""

        userChoice = self._get_user_choice("Order by")

        self.cur.execute(self.sql_select_all % (userChoice))
        results = self.cur.fetchall()

        # add iteration to print in new lines
        for employee in results:
            for attribute, data in zip(self.attributes, employee):
                print(attribute, data)
            print("\n  *********\n")

    def search_data(self):
        """Search for an employee by a specific field"""

        options = ["employeeID", "forename", "surname", "email"]
        userChoice = self._get_user_choice(options, "Search by")

        if userChoice == 0:
            query = self._get_employee_id()
        else:
            query = input("Enter search term: ")

        self.cur.execute(self.sql_search % options[userChoice], (query,))
        result = self.cur.fetchall()

        if not result:
            print("No records")

        # If only one record exists, put it in a list to have the same format with multiple results
        if isinstance(result, tuple):
            result = [result]

        for row in result:
            for index, detail in enumerate(row):
                if index == 0:
                    print("\nEmployee ID: " + str(detail))
                elif index == 1:
                    print("Employee Title: " + detail)
                elif index == 2:
                    print("Employee Name: " + detail)
                elif index == 3:
                    print("Employee Surname: " + detail)
                elif index == 4:
                    print("Employee Email: " + detail)
                else:
                    print("Salary: " + str(detail))

    def update_data(self):
        """Update a specific field of an employee record"""

        options = ["title", "forename", "surname", "email", "salary"]

        userChoice = self._get_user_choice(options, "Update")

        employeeID = self._get_employee_id()

        print("Enter new " + options[userChoice] + ": ", end='')
        change = input()

        if userChoice == 4:
            change = float(change)
            if change < 0:
                raise ValueError("Salary cannot be negative. Please try again.")

        updateQuery = self.sql_update_data % (options[userChoice])
        result = self.cur.execute(updateQuery, (change, employeeID))
        self.conn.commit()

        if result.rowcount != 0:
            print(str(result.rowcount) + " row(s) affected.")
        else:
            print("\nCannot find this record in the database")

    def delete_method(self, message):
        """Ask the user to confirm if they really want to proceed with deletion"""

        print(message)
        print("1. Yes")
        print("2. No, return to main menu")
        reallyDelete = int(input())
        return reallyDelete

    def delete_data(self):
        """Delete an employee record using their employee id"""

        employeeID = self._get_employee_id()
        reallyDelete = self.delete_method("\nAre you sure you want to delete this record?")

        if reallyDelete == 2:
            print("\nNo worries, returning to main menu.\n")
            return

        result = self.cur.execute(self.sql_delete_data, (employeeID,))
        self.conn.commit()

        if result.rowcount != 0:
            print(str(result.rowcount) + " row(s) affected.")
        else:
            print("\nCannot find this record in the database")

    def drop_table(self):
        """Delete all the employee data and the table"""
        reallyDelete = self.delete_method("\nThis action will permanently delete your table along with all "
                                          "employee data. Are you sure you want to continue?")
        if reallyDelete == 2:
            print("\nNo worries, returning to main menu.\n")
            return

        self.cur.execute(self.sql_drop_table)
        self.conn.commit()
        print("\nTable deleted successfully\n")


class Employee:
    def __init__(self):
        self.employeeID = 0
        self.empTitle = ''
        self.forename = ''
        self.surname = ''
        self.email = ''
        self.salary = 0.0

    def set_employee_id(self, employeeID):
        self.employeeID = employeeID

    def set_title(self, empTitle):
        self.empTitle = empTitle

    def set_forename(self, forename):
        self.forename = forename

    def set_surname(self, surname):
        self.surname = surname

    def set_email(self, email):
        self.email = email

    def set_salary(self, salary):
        self.salary = salary

    def get_employee_id(self):
        return self.employeeID

    def get_title(self):
        return self.empTitle

    def get_forename(self):
        return self.forename

    def get_surname(self):
        return self.surname

    def get_email(self):
        return self.email

    def get_salary(self):
        return self.salary

    def __str__(self):
        return self.empTitle + "\n" + self.forename + "\n" + self.surname + "\n" + self.email + "\n" + str(self.salary)


# The main function will parse arguments.
# These argument will be defined by the users on the console.
# The user will select a choice from the menu to interact with the database.

while True:
    print("\n Menu:")
    print("**********")
    print(" 1. Create table")
    print(" 2. Insert new employee record manually")
    print(" 3. Display all employee data")
    print(" 4. Import employee data from CSV file")
    print(" 5. Export all employee data to CSV file")
    print(" 6. Search for an employee record")
    print(" 7. Update an employee record")
    print(" 8. Delete an employee record")
    print(" 9. Delete all data")
    print(" 10. Exit\n")

    try:
        __choose_menu = int(input("Enter your choice: "))
        print()
    except ValueError:
        print("Please select a number from the options above.")
        continue

    db_ops = DBOperations()

    try:
        if __choose_menu == 1:
            db_ops.create_table()
        elif __choose_menu == 2:
            db_ops.insert_data()
        elif __choose_menu == 3:
            db_ops.select_all()
        elif __choose_menu == 4:
            db_ops.import_from_csv()
        elif __choose_menu == 5:
            db_ops.export_to_csv()
        elif __choose_menu == 6:
            db_ops.search_data()
        elif __choose_menu == 7:
            db_ops.update_data()
        elif __choose_menu == 8:
            db_ops.delete_data()
        elif __choose_menu == 9:
            db_ops.drop_table()
        elif __choose_menu == 10:
            exit(0)
        else:
            print("\nInvalid Choice")

    except Exception as e:
        print(e)
    finally:
        db_ops.conn.close()
