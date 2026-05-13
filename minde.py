import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTextEdit, QInputDialog
)
from PySide6.QtCore import Qt, QThread, Signal

import socket

HOST = "10.153.212.104"
PORT = 1357

muted_users = []


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
                    self.received.emit(data.decode("utf-8", errors="ignore"))
                else:
                    break
            except:
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

        layout = QVBoxLayout(self)
        self.setup_ui(layout)

        self.get_username()
        self.connect_to_server()

    def setup_ui(self, layout):
        title = QLabel("Goats🐐", alignment=Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(title)

        self.chat = QTextEdit()
        self.chat.setReadOnly(True)
        self.chat.setStyleSheet("background-color: #1e1e1e; color: #ffffff;")
        layout.addWidget(self.chat, stretch=1)

        input_layout = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("Skriv meddelande... (/mute namn | /unmute namn | /mutelist)")
        self.input.returnPressed.connect(self.send_message)

        send_btn = QPushButton("Skicka")
        send_btn.clicked.connect(self.send_message)

        input_layout.addWidget(self.input, stretch=1)
        input_layout.addWidget(send_btn)
        layout.addLayout(input_layout)

    def get_username(self):
        name, ok = QInputDialog.getText(self, "Användarnamn", "Ange ditt namn:")
        if ok and name.strip():
            self.username = name.strip()

    def connect_to_server(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((HOST, PORT))
            self.chat.append("Ansluten till servern!")
            self.chat.append(f"Inloggad som: {self.username}")

            self.receiver_thread = ReceiverThread(self.socket)
            self.receiver_thread.received.connect(self.handle_message)
            self.receiver_thread.start()
        except Exception as e:
            self.chat.append(f"Kunde inte ansluta: {e}")

    def is_muted(self, name):
        return name.lower() in [x.lower() for x in muted_users]

    def handle_message(self, text):
        if ":> " in text:
            raw_sender = text.split(":> ", 1)[0]
            # Plocka ut bara användarnamnet
            sender = raw_sender.split(": ")[-1].strip()
            if self.is_muted(sender):
                return  # Visa ingenting, hoppa över meddelandet

        self.chat.append(text)

    def send_message(self):
        if not self.socket:
            return

        msg = self.input.text().strip()
        if not msg:
            return

        # Visa mutelistan
        if msg.lower() == "/mutelist":
            if muted_users:
                users = ", ".join(muted_users)
                self.chat.append(f"🔇 Mutade användare: {users}")
            else:
                self.chat.append("🔇 Mutelistan är tom.")
            self.input.clear()
            return

        # Lägg till mute
        if msg.lower().startswith("/mute "):
            name = msg[6:].strip()
            if name:
                lower_name = name.lower()
                if lower_name not in [x.lower() for x in muted_users]:
                    muted_users.append(name)
                    self.chat.append(f"🔇 {name} är nu mutad.")
                else:
                    self.chat.append(f"⚠️ {name} är redan mutad.")
            self.input.clear()
            return

        # Ta bort mute
        if msg.lower().startswith("/unmute "):
            name = msg[8:].strip()
            if name:
                match = next((x for x in muted_users if x.lower() == name.lower()), None)
                if match:
                    muted_users.remove(match)
                    self.chat.append(f"🔊 {name} är nu unmutad.")
                else:
                    self.chat.append(f"⚠️ {name} finns inte i mutelistan.")
            self.input.clear()
            return

        # Vanligt meddelande
        try:
            self.chat.append(f"[{self.username}] {msg}")
            self.socket.sendall(f"{self.username}:> {msg}".encode("utf-8"))
            self.input.clear()
        except:
            pass

    def closeEvent(self, event):
        if self.receiver_thread:
            self.receiver_thread.stop()
        if self.socket:
            self.socket.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MyWindow()
    win.show()
    sys.exit(app.exec())