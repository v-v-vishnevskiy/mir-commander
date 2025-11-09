import logging

from mir_commander.ui import programs
from mir_commander.ui.errors import ProgramRegistrationError
from mir_commander.ui.program_manager import program_manager

logger = logging.getLogger("Startup.ProgramManager")


def startup():
    for item in programs.__all__:
        program_class = programs.__getattribute__(item)
        try:
            program_manager.register(program_class())
        except ProgramRegistrationError as e:
            logger.error("Failed to register `%s`: %s", program_class.__name__, e)
