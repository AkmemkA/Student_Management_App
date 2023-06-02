from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QLabel, QWidget, \
    QGridLayout, QLineEdit, QPushButton, QMainWindow, QDialog, QTableWidget, \
    QTableWidgetItem, QComboBox, QToolBar, QStatusBar, QMessageBox
from PyQt6.QtGui import QAction, QIcon
import sys
import sqlite3
import mysql.connector


class DatabaseConnection:
    """ Establishes a connection with database """

    def __init__(self, host="localhost", user="root", password="1234567890",
                 database="school"):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def connect(self):
        """ This method has to be called in order to connect to database"""
        connection = mysql.connector.connect(host=self.host, user=self.user,
                                             password=self.password,
                                             database=self.database)
        return connection


class MainWindow(QMainWindow):
    """ Main window class """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")

        # Creates top Menu
        file_menu_item = self.menuBar().addMenu("&File")
        edit_menu_item = self.menuBar().addMenu("&Edit")
        help_menu_item = self.menuBar().addMenu("&Help")

        # Top menu modification
        add_student_action = QAction(QIcon("add.png"), "Add Student", self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        search_action = QAction(QIcon("search.png"), "Search", self)
        edit_menu_item.addAction(search_action)
        search_action.triggered.connect(self.search)

        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        about_action.setMenuRole(QAction.MenuRole.NoRole)
        about_action.triggered.connect(self.about)

        # Creates a Toolbar
        toolbar = QToolBar(self)
        toolbar.addAction(add_student_action)
        toolbar.addAction(search_action)
        toolbar.setMovable(True)
        self.addToolBar(toolbar)

        # Creates a Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(
            ("ID", "Name", "Course", "Mobile"))
        self.table.verticalHeader().setVisible(False)
        self.setGeometry(350, 200, 720, 480)
        self.setCentralWidget(self.table)

        # Creates a Status Bar and adds elements
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Detects a click
        self.table.cellClicked.connect(self.cell_clicked)

    def cell_clicked(self):
        """ Executed when a cell is selected """
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)

        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)

        # Prevents buttons from appearing every time a cell is selected
        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.status_bar.removeWidget(child)

        self.status_bar.addWidget(edit_button)
        self.status_bar.addWidget(delete_button)

    def load_data(self):
        """ Loads data from database into a table """
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM students")
        result = cursor.fetchall()
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number,
                                   QTableWidgetItem(str(data)))
        connection.close()

    def insert(self):
        dialog = InsertDialog()
        dialog.exec()

    def search(self):
        dialog = SearchDialog()
        dialog.exec()

    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()

    def about(self):
        dialog = AboutDialog()
        dialog.exec()


class AboutDialog(QMessageBox):
    """ About dialog window """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        content = """
        This app was created as a training exercise for a Python course.
        Please feel free to send me your suggestions on improving the app
        at KODI199312@gmail.com
        """
        self.setText(content)


class InsertDialog(QDialog):
    """ New student dialog window """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("New Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Student Name Widget
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Add ComboBox of Courses
        self.student_course = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.student_course.addItems(courses)
        layout.addWidget(self.student_course)

        # Add Student Number
        self.student_phone_number = QLineEdit()
        self.student_phone_number.setPlaceholderText("Phone Number")
        layout.addWidget(self.student_phone_number)

        # Add a submit button
        add_button = QPushButton("Add")
        add_button.clicked.connect(self.add_student)
        layout.addWidget(add_button)

        self.setLayout(layout)

    def add_student(self):
        """ Called when new student is being added """
        name = self.student_name.text()
        course = self.student_course.itemText(
            self.student_course.currentIndex())
        mobile = self.student_phone_number.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (name, course, mobile) VALUES ("
                       "%s, %s, %s)", (name, course, mobile))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()

        self.close()


class SearchDialog(QDialog):
    """ Search dialog window """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Find a Student")
        self.setFixedWidth(300)
        self.setFixedHeight(150)

        layout = QVBoxLayout()

        # Search By Student Name Widget
        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText("Name to Search")
        layout.addWidget(self.student_name)

        # Create a search button
        add_button = QPushButton("Search")
        add_button.clicked.connect(self.search)
        layout.addWidget(add_button)

        self.setLayout(layout)

    def search(self):
        """ Called to search a student """
        name = self.student_name.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        items = main_window.table.findItems(name,
                                            Qt.MatchFlag.MatchFixedString)
        for item in items:
            main_window.table.item(item.row(), 1).setSelected(True)

        cursor.close()
        connection.close()
        self.close()


class EditDialog(QDialog):
    """ Edit dialog window """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Edit Student Record")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        index = main_window.table.currentRow()

        # Gets ID from selected row
        self.student_id = main_window.table.item(index, 0).text()

        # Student Name Widget
        student_name = main_window.table.item(index, 1).text()
        self.student_name = QLineEdit(student_name)
        self.student_name.setPlaceholderText("Name")
        layout.addWidget(self.student_name)

        # Add ComboBox of Courses
        course_name = main_window.table.item(index, 2).text()
        self.student_course = QComboBox()
        courses = ["Biology", "Math", "Astronomy", "Physics"]
        self.student_course.addItems(courses)
        self.student_course.setCurrentText(course_name)
        layout.addWidget(self.student_course)

        # Add Student Number
        student_number = main_window.table.item(index, 3).text()
        self.student_phone_number = QLineEdit(student_number)
        self.student_phone_number.setPlaceholderText("Phone Number")
        layout.addWidget(self.student_phone_number)

        # Add a submit button
        add_button = QPushButton("Update")
        add_button.clicked.connect(self.update)
        layout.addWidget(add_button)

        self.setLayout(layout)

    def update(self):
        """ Updates student information """
        name = self.student_name.text()
        course = self.student_course.itemText(
            self.student_course.currentIndex())
        mobile = self.student_phone_number.text()
        id = self.student_id
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name = %s, course = %s, mobile = "
                       "%s WHERE id = %s", (name, course, mobile, id))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()

        self.close()


class DeleteDialog(QDialog):
    """ Delete dialog window """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Edit Student Record")

        layout = QGridLayout()

        # Confirmation dialog
        confirmation = QLabel("Are you sure you want to delete the record?")
        yes = QPushButton("Yes")
        no = QPushButton("No")

        # Dialog layout
        layout.addWidget(confirmation, 0, 0, 1, 2)
        layout.addWidget(yes, 1, 0)
        layout.addWidget(no, 1, 1)
        self.setLayout(layout)

        yes.clicked.connect(self.delete_student)
        no.clicked.connect(self.close_dialog)

    def close_dialog(self):
        """ Called when No is triggered """
        self.reject()

    def delete_student(self):
        """ Called when Yes is triggered """
        # Gets selected row index and student ID
        index = main_window.table.currentRow()
        student_id = main_window.table.item(index, 0).text()

        # Deletes a record
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("DELETE from students WHERE id = %s", (student_id,))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()

        self.close()

        # Deletion confirmation window
        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setText("The record was deleted")
        confirmation_widget.exec()


app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
main_window.load_data()
sys.exit(app.exec())
