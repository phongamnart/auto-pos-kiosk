import sys
from PyQt5.QtGui import QPixmap
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication,QTableWidgetItem,QMessageBox,QPushButton
from PyQt5.QtCore import pyqtSlot, QFile, QTextStream
from PIL import ImageQt
import mysql.connector
import threading
import keyboard
import qrcode
import subprocess


from Home_ui import *
from Admin_ui import *
from Add_product_ui import *
from Show_ui import *
from welcome_ui import *
# from test import ArmControl

connection = mysql.connector.connect(
    host="localhost",
    user ="product",
    password="zxcasdqwe113",
    db="project_product"
)
cursor = connection.cursor()
# Start Class Mainwindow------------------------------------------------------------------------------------------------------------------------------
class HomeWindow(QMainWindow):
    def __init__(self):
        super(HomeWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.admin_button.clicked.connect(self.gotologin)
        self.ui.customer_button.clicked.connect(self.welcomee)
        self.setObjectName("home")
        self.setWindowIcon(QtGui.QIcon("001.jpg"))
        self.setMinimumSize(QtCore.QSize(1200, 800))
        self.setMaximumSize(QtCore.QSize(1200, 800))
        # link หน้า Admin
    def gotologin(self):
        login=Adminwindow()
        widget.addWidget(login)
        widget.setCurrentIndex(widget.currentIndex()+1)
        #  link หน้า welcome
    def welcomee(self):
        Welcome= welcome()
        widget.addWidget(Welcome)
        widget.setCurrentIndex(widget.currentIndex()+1)

#End Class MainWindow---------------------------------------------------------------------------------------------------------

# Strat class Welcome --------------------------------------------------------------------------------------------------------

class welcome(QMainWindow):
    def __init__(self):
        super(welcome,self).__init__()
        self.ui = Ui_WelcomeWindow()
        self.ui.setupUi(self)
        self.ui.nextButton.clicked.connect(self.customer)
        self.ui.backbutton_1.clicked.connect(self.backbutton)
        # self.ui.nextButton.clicked.connect(self.run_test_py)
        # link หน้า show_customer
    def customer(self):
        customer=customerwindow()
        widget.addWidget(customer)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def backbutton(self):
        customer=HomeWindow()
        widget.addWidget(customer)
        widget.setCurrentIndex(widget.currentIndex()+1)

    # def run_test_py():
    #     subprocess.Popen(["python", "test.py"]) 

# End class welcome ----------------------------------------------------------------------------------------------------------

# Start Class Admin_ui -------------------------------------------------------------------------------------------------------
class Adminwindow(QMainWindow):
    def __init__(self):
        super(Adminwindow, self).__init__()
        self.ui = Ui_Admin()
        self.ui.setupUi(self)
        self.setObjectName("Admin")
        self.setWindowIcon(QtGui.QIcon("001.jpg"))
        self.setMinimumSize(QtCore.QSize(1200, 800))
        self.setMaximumSize(QtCore.QSize(1200, 800))
        self.ui.loginButton.clicked.connect(self.login)
        self.ui.Backbutton.clicked.connect(self.backbutton2)
    # algorithm login
    def login(self):
        username = self.ui.username_input.text()
        password = self.ui.password_input.text()
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user ="product",
                password="zxcasdqwe113",
                db="project_product"
            )
            cursor = connection.cursor()
            query = "SELECT * FROM admin WHERE username = %s AND password = %s"
            cursor.execute(query, (username, password))
            user = cursor.fetchone()

            if user:
                QMessageBox.information(self, 'Login Successful', 'Welcome, {}'.format(username))
                self.open_add_productWindow()
                self.ui.username_input.clear()
                self.ui.password_input.clear()
            else:
                QMessageBox.warning(self, 'Login Failed', 'Invalid username or password. Please try again.')
                self.ui.password_input.clear()
            cursor.close()
            connection.close()

        except mysql.connector.Error as err:
            print("Error: {}".format(err))
        # link หน้า addProduct
    def open_add_productWindow(self):
        self.add_product_window = add_productWindow()
        self.add_product_window.show()

    def backbutton2(self):
        customer=HomeWindow()
        widget.addWidget(customer)
        widget.setCurrentIndex(widget.currentIndex()+1)


# End Class Admin_ui -------------------------------------------------------------------------------------------------



# Class of Add_product_ui---------------------------------------------------------------------------------------------
class add_productWindow(QMainWindow):
    def __init__(self):
        super(add_productWindow, self).__init__()
        self.ui = Ui_Add_product()
        self.ui.setupUi(self)
        self.setObjectName("Add_Product")
        self.setWindowIcon(QtGui.QIcon("001.jpg"))
        self.setMinimumSize(QtCore.QSize(1200, 800))
        self.setMaximumSize(QtCore.QSize(1200, 800))
        self.ui.AddButton.clicked.connect(self.add_product)
        self.ui.LoadButton.clicked.connect(self.load_data)


    # algorithm addproduct
    def add_product(self):
        name = self.ui.name_input.text()
        barcode = self.ui.barcode_input.text()
        price = self.ui.price_input.text()
        quantity = self.ui.quantity_input.text()
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user ="product",
                password="zxcasdqwe113",
                db="project_product"
            )
            cursor = connection.cursor()

            query = """
                INSERT INTO product (NameProduct, Barcode, Price, Quantity)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                NameProduct = VALUES(NameProduct),
                Price = VALUES(Price),
                Quantity = VALUES(Quantity)
                """
            cursor.execute(query, (name, barcode, price, quantity))
            connection.commit()


            print("commit success :",name + barcode + price + quantity)

            QMessageBox.information(self, 'Success', 'Product added successfully.')
            self.clear_inputs() 

            cursor.close()
            connection.close()

            self.load_data()

        except mysql.connector.Error as err:
            print("Error: {}".format(err))
            QMessageBox.warning(self, 'Error', 'An error occurred while adding the product.')
    # load data
    def load_data(self):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user ="product",
                password="zxcasdqwe113",
                db="project_product"
            )
            cursor = connection.cursor()

            query = "SELECT NameProduct, Barcode, Price, Quantity FROM product"
            cursor.execute(query)
            resalt = cursor.fetchall()

            self.ui.tableWidget.setRowCount(0)

            for row_number, row_data in enumerate(resalt):
                self.ui.tableWidget.insertRow(row_number)

                for column_number, data in enumerate(row_data):
                    self.ui.tableWidget.setItem(row_number, column_number, QTableWidgetItem(str(data)))

                    delete_button = QPushButton('Delete', self)
                    delete_button.clicked.connect(lambda _, row=row_number: self.delete_product(row))
                    self.ui.tableWidget.setCellWidget(row_number, 4, delete_button)
            cursor.close()
            connection.close()

        except mysql.connector.Error as err:
            print("Error: {}".format(err))
            QMessageBox.warning(self, 'Error', 'An error occurred while loading data.')

    # delete data
    def delete_product(self,row):  
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user ="product",
                password="zxcasdqwe113",
                db="project_product"
            )
            cursor = connection.cursor()
            barcode = self.ui.tableWidget.item(row, 1).text()
            reply = QMessageBox.question(self, 'Delete Confirmation', f'Do you want to delete the product "{barcode}"?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                query = "DELETE FROM product WHERE Barcode = %s"
                cursor.execute(query, (barcode,))
                connection.commit()

                self.load_data()

                QMessageBox.information(self, 'Success', 'Product deleted successfully.')
            else:
                QMessageBox.information(self, 'Delete Cancelled', 'Product deletion cancelled.')

            cursor.close()
            connection.close()

        except mysql.connector.Error as err:
            print("Error: {}".format(err))
            QMessageBox.warning(self, 'Error', 'An error occurred while deleting the product.')
    # clear input 
    def clear_inputs(self):
        self.ui.name_input.clear()
        self.ui.barcode_input.clear()
        self.ui.price_input.clear()
        self.ui.quantity_input.clear()

# End Class Add_product_ui ---------------------------------------------------------------------------------------------------------------------------------------------


# Start Class Customer_show---------------------------------------------------------------------------------------------------------------------------------------------

class customerwindow(QMainWindow):
    def __init__(self):
        super(customerwindow, self).__init__()
        self.ui =  Ui_show2()
        self.ui.setupUi(self)
        self.total_price = 0
        self.ui.payButton.clicked.connect(self.generate_qr_code) #use generated qrcode
        self.setObjectName("Customer")
        self.setWindowIcon(QtGui.QIcon("001.jpg"))
        self.setMinimumSize(QtCore.QSize(1200, 800))
        self.setMaximumSize(QtCore.QSize(1200, 800))
        self.scanner_thread = ScannerThread(self.scan_product)
        self.scanner_thread.start()
        self.last_scanned_barcode = None
        self.current_quantity = None



    def scan_product(self, barcode):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="product",
                password="zxcasdqwe113",
                db="project_product"
            )

            cursor = connection.cursor()
            query = "SELECT NameProduct, Price FROM product WHERE barcode = %s"
            cursor.execute(query, (barcode,))
            data = cursor.fetchone()

            if data is not None:
                name_product, price = data

                # หาค่า rowPosition ของรายการที่มีชื่อสินค้าเดิม
                rowPosition = self.find_row_by_name(name_product)

                if rowPosition is not None:
                    # หากมีรายการที่มีชื่อสินค้าเดิมในตาราง ให้อัปเดตปริมาณ (quantity)
                    current_quantity_item = self.ui.tableWidget.item(rowPosition, 2)
                    if current_quantity_item is not None:
                        current_quantity = int(current_quantity_item.text())
                        current_quantity += 1
                        current_quantity_item.setText(str(current_quantity))
                        # คำนวณราคาทั้งหมดและแสดงใน Label แสดงผลราคาทั้งหมด
                        self.total_price += price
                        self.ui.total_label.setText(f'Total : {self.total_price:.2f} Bath')
                else:
                    # หากไม่มีรายการที่มีชื่อสินค้าเดิมในตาราง ให้เพิ่มรายการใหม่
                    rowPosition = self.ui.tableWidget.rowCount()
                    self.ui.tableWidget.insertRow(rowPosition)
                    self.ui.tableWidget.setItem(rowPosition, 0, QTableWidgetItem(name_product))
                    self.ui.tableWidget.setItem(rowPosition, 1, QTableWidgetItem(str(price)))
                    self.ui.tableWidget.setItem(rowPosition, 2, QTableWidgetItem('1'))
                    # คำนวณราคาทั้งหมดและแสดงใน Label แสดงผลราคาทั้งหมด
                    self.total_price += price
                    self.ui.total_label.setText(f'Total : {self.total_price:.2f} Bath')

                # อัปเดต Barcode ที่แสกนล่าสุด
                self.last_scanned_barcode = barcode
                self.ui.order_label.setText(f'Name : {name_product} Amount : {price}')
            else:
                result_text = f'Not found barcode: {barcode}'
                self.ui.result_label.setText(result_text)
                self.ui.order_label.setText('Name:')

        except mysql.connector.Error as err:
            print("Error: {}".format(err))
            QMessageBox.warning(self, 'Error', 'An error occurred while scanning the barcode.')

    def find_row_by_name(self, name):
        # ค้นหารายการที่มีชื่อสินค้าเดิมในตารางและคืนค่า rowPosition
        row_count = self.ui.tableWidget.rowCount()
        for row in range(row_count):
            item = self.ui.tableWidget.item(row, 0)
            if item is not None and item.text() == name:
                return row
        return None
    
    def generate_qr_code(self):
        data = f'Total : {self.total_price:.2f} Bath'

        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(data)
        qr.make(fit=True)

        # สร้างรูปภาพ QR Code
        img = qr.make_image(fill_color="black", back_color="white")

        # แปลงรูปภาพให้กลายเป็น QPixmap
        qt_img = ImageQt.toqpixmap(ImageQt.Image.fromqimage(ImageQt.toqimage(img)))
        pixmap = QPixmap(qt_img)

        # แสดงรูปภาพ QR Code ใน QLabel
        self.ui.qr_label.setPixmap(pixmap)
        self.ui.qr_label.setAlignment(QtCore.Qt.AlignCenter)


class ScannerThread(threading.Thread):
    def __init__(self, callback):
        threading.Thread.__init__(self)
        self.callback = callback

    def run(self):
        barcode_value = ""
        while True:
            event = keyboard.read_event(suppress=True)
            if event.event_type == keyboard.KEY_DOWN:
                if event.name == "enter":
                    self.callback(barcode_value)
                    barcode_value = ""
                else:
                    barcode_value += event.name



# End Class Customer_show-----------------------------------------------------------------------------------------------------------------------------------------------

# Start class payment *-------------------------------------------------------------------------------------------------------------------------------------------------


# End class payment -----------------------------------------------------------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    app = QApplication(sys.argv)
    style_file = QFile("style.qss")
    style_file.open(QFile.ReadOnly | QFile.Text)
    style_stream = QTextStream(style_file)
    app.setStyleSheet(style_stream.readAll())
    main = HomeWindow()
    widget = QtWidgets.QStackedWidget()
    widget.addWidget(main)
    widget.show()
     
    sys.exit(app.exec())