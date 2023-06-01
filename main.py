from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QLabel, QWidget, \
    QGridLayout, QLineEdit, QPushButton, QMainWindow, QDialog, QTableWidget, \
    QTableWidgetItem, QComboBox, QToolBar, QStatusBar, QMessageBox
from PyQt6.QtGui import QAction, QIcon
import sys
import sqlite3


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Student Management System")

        # Creates top Menu
        file_menu_item = self.menuBar().addMenu("&File")
        edit_menu_item = self.menuBar().addMenu("&Edit")
        help_menu_item = self.menuBar().addMenu("&Help")

        add_student_action = QAction(QIcon("add.png"), "Add Student", self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        search_action = QAction(QIcon("search.png"), "Search", self)
        edit_menu_item.addAction(search_action)
        search_action.triggered.connect(self.search)

        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        about_action.setMenuRole(QAction.MenuRole.NoRole)

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
        self.table.cellClicked.connect(self. cell_clicked)


    def cell_clicked(self):
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)

        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)

        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.status_bar.removeWidget(child)

        self.status_bar.addWidget(edit_button)
        self.status_bar.addWidget(delete_button)


    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()


    def load_data(self):
        connection = sqlite3.connect("database.db")
        result = connection.execute("SELECT * FROM students")
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


class InsertDialog(QDialog):
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
        name = self.student_name.text()
        course = self.student_course.itemText(
            self.student_course.currentIndex())
        mobile = self.student_phone_number.text()
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("INSERT INTO students (name, course, mobile) VALUES ("
                       "?, ?, ?)", (name, course, mobile))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()

        self.close()


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Find a Student")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

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
        name = self.student_name.text()
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        items = main_window.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            main_window.table.item(item.row(), 1).setSelected(True)

        cursor.close()
        connection.close()
        self.close()


class EditDialog(QDialog):
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
        name = self.student_name.text()
        course = self.student_course.itemText(
            self.student_course.currentIndex())
        mobile = self.student_phone_number.text()
        id = self.student_id
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("UPDATE students SET name = ?, course = ?, mobile = ? "
                       "WHERE id = ?", (name, course, mobile, id))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()

        self.close()


class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Edit Student Record")

        layout = QGridLayout()

        confirmation = QLabel("Are you sure you want to delete the record?")
        yes = QPushButton("Yes")
        no = QPushButton("No")

        layout.addWidget(confirmation, 0, 0, 1, 2)
        layout.addWidget(yes, 1, 0)
        layout.addWidget(no, 1, 1)
        self.setLayout(layout)

        yes.clicked.connect(self.delete_student)
        no.clicked.connect(self.close_dialog)

    def close_dialog(self):
        self.reject()

    def delete_student(self):
        # Gets selected row index and student ID
        index = main_window.table.currentRow()
        student_id = main_window.table.item(index, 0).text()

        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("DELETE from students WHERE id = ?", (student_id, ))
        connection.commit()
        cursor.close()
        connection.close()
        main_window.load_data()

        self.close()

        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setText("The record was deleted")
        confirmation_widget.exec()

    def not_deleted(self):
        pass



app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
main_window.load_data()
sys.exit(app.exec())
