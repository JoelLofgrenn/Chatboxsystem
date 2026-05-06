import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QInputDialog
)
from PySide6.QtCore import Qt, QThread, Signal

import socket

HOST = "10.154.1.24"
PORT = 1357

list = []


class ReceiverThread(QThread):
    received = Signal(str)

    def __init__(self, sock):
        super().__init__()
        self.sock = sock
        self.running = True

    def run(self):
        while self.running:
            try:
                data = self.sock.recv(1024)
                if data:
                    message = data.decode("utf-8", errors="ignore")
                    self.received.emit(message)
                else:
                    break
            except Exception:
                break

    def stop(self):
        self.running = False
        self.quit()
        self.wait()


class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chat System: Created by Goats🐐")
        self.resize(700, 600)

        self.socket = None
        self.receiver_thread = None
        self.username = "Anonym"

        self.layout = QVBoxLayout(self)
        self.setup_ui()

        self.get_username()
        self.connect_to_server()

    def get_username(self):
        """Användaren skriver själv in sitt användarnamn"""
        username, ok = QInputDialog.getText(
            self, 
            "Välkommen till chatten",
            "Ange ditt användarnamn:",
        )
        if ok and username.strip():
            self.username = username.strip()


    def setup_ui(self):
        self.maintitle = QLabel("Goats🐐", alignment=Qt.AlignCenter)
        self.maintitle.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.layout.addWidget(self.maintitle)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("background-color: #1e1e1e; color: #ffffff; font-family: Consolas;")
        self.layout.addWidget(self.chat_display, stretch=1)

        input_layout = QHBoxLayout()
        self.inputbox = QLineEdit()
        self.inputbox.setPlaceholderText("Skriv meddelande här och tryck Enter...")
        self.inputbox.returnPressed.connect(self.send_message)

        self.send_button = QPushButton("Skicka")
        self.send_button.clicked.connect(self.send_message)

        input_layout.addWidget(self.inputbox, stretch=1)
        input_layout.addWidget(self.send_button)
        self.layout.addLayout(input_layout)

        self.buttonone = QPushButton("Fortnite (skicka testmeddelande)")
        self.buttonone.clicked.connect(self.send_test_message)
        self.layout.addWidget(self.buttonone)

    def connect_to_server(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((HOST, PORT))
            self.chat_display.append("<span style='color: lime;'>Ansluten till servern!</span>")
            self.chat_display.append(f"<span style='color: cyan;'>Inloggad som: <b>{self.username}</b></span>")

            self.receiver_thread = ReceiverThread(self.socket)
            self.receiver_thread.received.connect(self.display_message)
            self.receiver_thread.start()

        except Exception as e:
            self.chat_display.append(f"<span style='color: red;'>Kunde inte ansluta: {e}</span>")

    def display_message(self, text: str):
        self.chat_display.append(text)

    def send_message(self):
        if not self.socket:
            self.chat_display.append("<span style='color: red;'>Inte ansluten!</span>")
            return
        
        if message.startswith() == "/mute":
            append.list

        message = self.inputbox.text().strip()
        if not message:
            return

        full_message = f"{self.username}:> {message}"

        try:
            
            self.chat_display.append(f"<b style='color: #00ff88;'>[{self.username}]</b> {message}")

            
            self.socket.sendall(full_message.encode("utf-8"))

            self.inputbox.clear()

        except Exception as e:
            self.chat_display.append(f"<span style='color: red;'>Fel vid sändning: {e}</span>")

    def send_test_message(self):
        self.inputbox.setText("R6 gods right here (2-7 mot the LDP Boys)")
        self.send_message()

    def closeEvent(self, event):
        if self.receiver_thread:
            self.receiver_thread.stop()
        if self.socket:
            self.socket.close()
        event.accept()

    


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())