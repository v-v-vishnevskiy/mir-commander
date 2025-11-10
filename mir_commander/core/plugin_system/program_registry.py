import logging
from typing import Iterable

from mir_commander.api.program import ControlPanel, Program, ProgramConfig, ProgramPlugin
from mir_commander.core.errors import ProgramRegistrationError, UndefinedProgramError

logger = logging.getLogger("Core.ProgramRegistry")


class ProgramRegistry:
    def __init__(self):
        self._programs: dict[str, ProgramPlugin] = {}

    def _get_program(self, program_id: str) -> ProgramPlugin:
        try:
            return self._programs[program_id]
        except KeyError:
            raise UndefinedProgramError()

    @property
    def programs(self) -> Iterable[ProgramPlugin]:
        return self._programs.values()

    def register(self, program: ProgramPlugin):
        program_id = program.get_id()

        if type(program_id) is not str or len(program_id) == 0:
            raise ProgramRegistrationError(f"Invalid program id: {program_id}")

        self._programs[program_id] = program
        logger.debug("`%s` program registered", program.get_metadata().name)

    def get_program(self, progrma_id: str) -> ProgramPlugin:
        return self._get_program(progrma_id)

    def get_config_class(self, program_id: str) -> type[ProgramConfig]:
        return self._get_program(program_id).get_config_class()

    def get_program_class(self, program_id: str) -> type[Program]:
        return self._get_program(program_id).get_program_class()

    def get_control_panel_class(self, program_id: str) -> None | type[ControlPanel]:
        return self._get_program(program_id).get_control_panel_class()
