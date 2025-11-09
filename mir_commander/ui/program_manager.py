import logging
from typing import Iterable

from mir_commander.api.program import ControlPanel, Program, ProgramConfig, ProgramPlugin
from mir_commander.ui.errors import ProgramRegistrationError, UndefinedProgramError

logger = logging.getLogger("UI.ProgramManager")


class ProgramManager:
    def __init__(self):
        self._programs: dict[str, ProgramPlugin] = {}

    def _get_program(self, name: str) -> ProgramPlugin:
        try:
            return self._programs[name]
        except KeyError:
            raise UndefinedProgramError()

    @property
    def programs(self) -> Iterable[ProgramPlugin]:
        return self._programs.values()

    def register(self, program: ProgramPlugin):
        name = program.get_name()

        if type(name) is not str or len(name) == 0:
            raise ProgramRegistrationError(f"Invalid program name: {name}")

        self._programs[name] = program
        logger.debug("`%s` program registered", program.get_name())

    def get_program(self, name: str) -> ProgramPlugin:
        return self._get_program(name)

    def get_config_class(self, name: str) -> type[ProgramConfig]:
        return self._get_program(name).get_config_class()

    def get_program_class(self, name: str) -> type[Program]:
        return self._get_program(name).get_program_class()

    def get_control_panel_class(self, name: str) -> None | type[ControlPanel]:
        return self._get_program(name).get_control_panel_class()


program_manager = ProgramManager()
