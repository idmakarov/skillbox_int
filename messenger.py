from datetime import datetime

import requests
from PyQt5 import QtWidgets, QtCore

from clientui import Ui_MainWindow


class Messenger(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self, url):
        super().__init__()
        self.setupUi(self)

        self.url = url
        self.after_id = -1
        self.server_failed = False

        self.pushButton.pressed.connect(self.button_pressed)

        self.load_messages()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_messages)
        self.timer.start(1000)

    def pretty_print(self, message):
        dt = datetime.fromtimestamp(message['timestamp'])
        dt = dt.strftime('%Y/%m/%d %H:%M:%S')
        first_line = dt + '  @' + message['name']
        second_line = message['text']
        self.textBrowser.append(first_line)
        self.textBrowser.append(second_line)
        self.textBrowser.append('')

    def update_messages(self):
        response = None
        server_f = self.server_failed

        try:
            response = requests.get(self.url + '/messages',
                                    params={'after_id': self.after_id})
            self.server_failed = False
        except:
            self.server_failed = True

        if not server_f and self.server_failed:
            server_fail_msg = 'Соединение с сервером потеряно...'
            self.textBrowser.append(server_fail_msg)
        elif server_f and not self.server_failed:
            server_recon_msg = 'Соединение с сервером восстановлено!'
            self.textBrowser.append(server_recon_msg)
            self.textBrowser.append('')

        if response and response.status_code == 200:
            messages = response.json()['messages']
            for message in messages:
                self.pretty_print(message)
                self.after_id = message['id']

            return messages

    def load_messages(self):
        while self.update_messages():
            pass

    def button_pressed(self):
        name = self.lineEdit.text()
        text = self.textEdit.toPlainText()
        data = {'name': name, 'text': text}

        response = None
        try:
            response = requests.post(self.url + '/send', json=data)
        except:
            pass

        if response and response.status_code == 200:
            self.textEdit.clear()
        else:
            err_msg = 'При отправке возникла ошибка!'
            self.textBrowser.append(err_msg)
            self.textBrowser.append('')


app = QtWidgets.QApplication([])
window = Messenger(url='http://127.0.0.1:5000')
window.show()
app.exec_()
