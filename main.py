import json
import datetime
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QListWidget, QMessageBox, QDialog, QDialogButtonBox


class Note:
    def __init__(self, title, description, deadline):
        self.title = title
        self.description = description
        self.deadline = deadline
        self.created_at = datetime.datetime.now()

    def format_deadline(self):
        remaining_time = self.deadline - datetime.datetime.now()
        return str(remaining_time)


class NoteApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Note App")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.notes_list = QListWidget()
        self.layout.addWidget(self.notes_list)

        self.create_note_widget = QWidget()
        self.create_note_layout = QHBoxLayout()
        self.create_note_widget.setLayout(self.create_note_layout)
        self.layout.addWidget(self.create_note_widget)

        self.title_input = QLineEdit()
        self.description_input = QLineEdit()
        self.deadline_input = QLineEdit()
        self.create_button = QPushButton("Create")
        self.create_note_layout.addWidget(QLabel("Title:"))
        self.create_note_layout.addWidget(self.title_input)
        self.create_note_layout.addWidget(QLabel("Description:"))
        self.create_note_layout.addWidget(self.description_input)
        self.create_note_layout.addWidget(QLabel("Deadline:"))
        self.create_note_layout.addWidget(self.deadline_input)
        self.create_note_layout.addWidget(self.create_button)

        self.delete_button = QPushButton("Delete")
        self.edit_button = QPushButton("Edit")
        self.layout.addWidget(self.delete_button)
        self.layout.addWidget(self.edit_button)

        self.notes = []
        self.load_notes()

        self.notes_list.itemClicked.connect(self.show_note_details)
        self.create_button.clicked.connect(self.create_note)
        self.delete_button.clicked.connect(self.delete_note)
        self.edit_button.clicked.connect(self.edit_note)

    def load_notes(self):
        try:
            with open("notes.json", "r") as json_file:
                notes_data = json.load(json_file)
                for note_data in notes_data:
                    title = note_data["title"]
                    description = note_data["description"]
                    deadline = datetime.datetime.fromisoformat(note_data["deadline"])
                    note = Note(title, description, deadline)
                    self.notes.append(note)
                    self.notes_list.addItem(note.title)
        except FileNotFoundError:
            pass

    def save_notes(self):
        notes_data = []
        for note in self.notes:
            note_data = {"title": note.title,
                         "description": note.description,
                         "deadline": note.deadline.isoformat()}
            notes_data.append(note_data)
        with open("notes.json", "w") as json_file:
            json.dump(notes_data, json_file)

    def create_note(self):
        title = self.title_input.text()
        description = self.description_input.text()
        deadline_str = self.deadline_input.text()
        try:
            deadline = datetime.datetime.strptime(deadline_str, "%Y-%m-%d %H:%M:%S")
            note = Note(title, description, deadline)
            self.notes.append(note)
            self.notes_list.addItem(note.title)
            self.title_input.clear()
            self.description_input.clear()
            self.deadline_input.clear()
            self.save_notes()
        except ValueError:
            QMessageBox.warning(self, "Invalid Date Format",
                            "Please enter the deadline date and time in the format 'YYYY-MM-DD HH:MM:SS'.")

    def delete_note(self):
        selected_items = self.notes_list.selectedItems()
        if selected_items:
            selected_item = selected_items[0]
            note_title = selected_item.text()

            reply = QMessageBox.question(self, "Delete Note",
                                         f"Are you sure you want to delete the note '{note_title}'?",
                                         QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                selected_row = self.notes_list.row(selected_item)
                self.notes_list.takeItem(selected_row)

                for note in self.notes:
                    if note.title == note_title:
                        self.notes.remove(note)
                        break

                self.save_notes()

    def edit_note(self):
        selected_items = self.notes_list.selectedItems()
        if selected_items:
            selected_item = selected_items[0]
            note_title = selected_item.text()

            for note in self.notes:
                if note.title == note_title:
                    dialog = EditNoteDialog(note)
                    if dialog.exec():
                        note.title = dialog.title_input.text()
                        note.description = dialog.description_input.text()
                        deadline_str = dialog.deadline_input.text()
                        note.deadline = datetime.datetime.strptime(deadline_str, "%Y-%m-%d %H:%M:%S")

                        selected_item.setText(note.title)
                        self.save_notes()
                    break

    def show_note_details(self, item):
        note_title = item.text()
        for note in self.notes:
            if note.title == note_title:
                details_msg = f"Title: {note.title}\n" \
                    f"Description: {note.description}\n" \
                    f"Deadline: {note.deadline}\n" \
                    f"Created At: {note.created_at}\n" \
                    f"Remaining Time: {note.format_deadline()}"
                QMessageBox.information(self, "Note Details", details_msg)


class EditNoteDialog(QDialog):
    def __init__(self, note):
        super().__init__()
        self.setWindowTitle("Edit Note")

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.title_input = QLineEdit(note.title)
        self.description_input = QLineEdit(note.description)
        self.deadline_input = QLineEdit(note.deadline.strftime("%Y-%m-%d %H:%M:%S"))

        layout.addWidget(QLabel("Title:"))
        layout.addWidget(self.title_input)
        layout.addWidget(QLabel("Description:"))
        layout.addWidget(self.description_input)
        layout.addWidget(QLabel("Deadline:"))
        layout.addWidget(self.deadline_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)


if __name__ == "__main__":\
    app = QApplication([])
    note_app = NoteApp()
    note_app.show()
    app.exec()
