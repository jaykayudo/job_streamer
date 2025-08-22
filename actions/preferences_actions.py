from actions.base import BaseAction
from client.base.interactor import BaseInteractor
from utils.types import MessageType
from utils.logging import JobStreamerLogger
from typing import List
from services.database.preference import PreferenceService
from utils.types import MessageTitle
from utils.validation import is_valid_option_index_based
from tabulate import tabulate

logger = JobStreamerLogger().get_logger()


class PreferencesActions(BaseAction):
    def __init__(self, interactor: BaseInteractor):
        super().__init__(interactor)

        self.actions = {
            "delete": self.delete_preference,
            "list": self.list_preferences,
        }

    @classmethod
    def get_actions(cls) -> List[str]:
        """
        Get the actions of the preference action class.
        """
        return ["delete", "list"]

    def delete_preference(self):
        """
        Delete a preference.
        """
        self.interactor.writer(MessageType.INFO, "Deleting a preference...")
        preferences = PreferenceService.get_preferences()
        preferences_dumped = [preference.json_dump() for preference in preferences]
        preferences_string = "\n".join(
            [f"{idx + 1}. {preference}" for idx, preference in enumerate(preferences)]
        )
        self.interactor.writer(
            MessageType.INFO,
            f"Please select a preference:\n{preferences_string}",
            title=MessageTitle.PREFERENCE_LIST,
            extra_context=preferences_dumped,
        )
        preference_index = self.interactor.reader(
            prompt="Enter the number of the preference"
        )
        if not is_valid_option_index_based(preference_index, preferences):
            self.interactor.writer(MessageType.ERROR, "Invalid option")
            return
        preference = preferences[int(preference_index) - 1]
        try:
            PreferenceService.delete_preference(preference.id)
            logger.info(f"Preference deleted successfully: {preference.name}")
            self.interactor.writer(
                MessageType.SUCCESS,
                f"Preference deleted successfully: {preference.name}",
            )
        except Exception as e:
            logger.error(f"Error deleting preference: {e}")
            self.interactor.writer(MessageType.ERROR, f"Error deleting preference: {e}")
            return

    def list_preferences(self):
        """
        List all preferences.
        """
        self.interactor.writer(MessageType.INFO, "Listing all preferences...")
        preferences = PreferenceService.get_preferences()
        preferences_dumped = [preference.json_dump() for preference in preferences]
        tabulated_data = tabulate(preferences_dumped, headers="keys", tablefmt="grid")
        self.interactor.writer(
            MessageType.INFO,
            tabulated_data,
            title=MessageTitle.PREFERENCE_LIST,
            extra_context=preferences_dumped,
        )
