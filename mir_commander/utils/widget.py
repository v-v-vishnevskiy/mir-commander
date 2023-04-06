from PySide6.QtCore import QEvent


class Translator:
    def retranslate_ui(self):
        pass

    def changeEvent(self, event: QEvent):
        if event.type() == QEvent.LanguageChange:
            self.retranslate_ui()
        super().changeEvent(event)  # type: ignore
