from automation.core.automator.base import BaseAutomator
from automation.core.automator.mock import MockAutomator
from conf.settings import ModulesName, Modules

AUTOMATORS = {
    ModulesName.WORKABLE.value: MockAutomator,
    ModulesName.WELLFOUND.value: MockAutomator,
    ModulesName.WEB3_CAREER.value: MockAutomator,
}

def get_automator_by_name(name: Modules) -> BaseAutomator:
    """
    Get an automator by name.
    """
    automator_class = AUTOMATORS.get(name)
    if not automator_class:
        raise ValueError(f"Automator {name} not found")
    return automator_class