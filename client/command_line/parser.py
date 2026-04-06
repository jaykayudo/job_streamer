from actions.application_actions import ApplicationActions
from actions.bio_actions import BioActions
from actions.help_actions import HelpActions
from actions.preferences_actions import PreferencesActions
from actions.project_actions import ProjectActions
from actions.resume_actions import ResumeActions
from actions.work_experience_actions import WorkExperienceActions

# Maps the top-level command word the user types → the corresponding action class.
COMMAND_MAP = {
    "bio": BioActions,
    "resume": ResumeActions,
    "application": ApplicationActions,
    "preference": PreferencesActions,
    "project": ProjectActions,
    "work_experience": WorkExperienceActions,
    "help": HelpActions,
}


def parse_input(text: str) -> tuple[str, str] | None:
    """
    Split raw user input into (group, subcommand).

    Examples
    --------
    "bio create"     -> ("bio", "create")
    "help"           -> ("help", "")
    ""               -> None
    """
    parts = text.strip().split(maxsplit=1)
    if not parts:
        return None
    group = parts[0].lower()
    subcommand = parts[1].lower() if len(parts) > 1 else ""
    return group, subcommand


def get_completions() -> list[str]:
    """Return every valid 'group subcommand' string for autocomplete."""
    completions: list[str] = []
    for group, action_cls in COMMAND_MAP.items():
        subactions = action_cls.get_actions()
        if subactions:
            for sub in subactions:
                completions.append(f"{group} {sub}")
        else:
            completions.append(group)
    return completions
