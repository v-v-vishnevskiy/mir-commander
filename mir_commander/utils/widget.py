from PySide6.QtCore import QEvent


class Translator:
    """Translator class.

    A special class, which implements changeEvent handler.
    Classes implementing widgets with translatable elements
    must inherit this class.
    """

    def retranslate_ui(self):
        pass

    def changeEvent(self, event: QEvent):
        """Handling only LanguageChange events and calling retranslate_ui"""

        if event.type() == QEvent.LanguageChange:
            self.retranslate_ui()
        super().changeEvent(event)  # type: ignore
