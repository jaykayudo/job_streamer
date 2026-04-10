from storage.core.models import SavedPreference, Category
from typing import List
from storage.core.engine import session
from conf.settings import Modules


class PreferenceService:
    @classmethod
    def get_preferences(cls) -> List[SavedPreference]:
        """
        Get all preferences from the database
        """
        return session.query(SavedPreference).all()

    @classmethod
    def get_or_create_category(cls, name: str) -> Category:
        """
        Get or create a category in the database
        """
        category = Category.get_or_create(name=name)
        return category

    @classmethod
    def create_preference(
        cls, name: str, module_name: Modules, preferences: List[str]
    ) -> SavedPreference:
        """
        Create a preference in the database
        """
        categories = [cls.get_or_create_category(name) for name in preferences]
        preference = SavedPreference(name=name, module_name=module_name)
        preference.save()
        preference.preferences.extend(categories)
        preference.save()
        # session.refresh(preference)
        return preference

    @classmethod
    def add_category_to_preference(cls, preference_id: str, category_name: str) -> bool:
        """
        Add a category to a preference
        """
        preference = session.query(SavedPreference).filter_by(id=preference_id).first()
        if not preference:
            return False
        category = cls.get_or_create_category(category_name)
        preference.preferences.append(category)
        preference.save()
        session.refresh(preference)
        return True

    @classmethod
    def remove_category_from_preference(
        cls, preference_id: str, category_name: str
    ) -> bool:
        """
        Remove a category from a preference
        """
        preference: SavedPreference = (
            session.query(SavedPreference).filter_by(id=preference_id).first()
        )
        if not preference:
            return False
        category = cls.get_or_create_category(category_name)
        preference.preferences.remove(category)
        preference.save()
        session.refresh(preference)
        return True

    @classmethod
    def get_preference(cls, name: str) -> SavedPreference | None:
        """
        Get a preference from the database by name
        """
        return session.query(SavedPreference).filter_by(name=name).first()

    @classmethod
    def get_preference_by_id(cls, preference_id: str) -> SavedPreference | None:
        """
        Get a preference from the database by id
        """
        return session.query(SavedPreference).filter_by(id=preference_id).first()

    @classmethod
    def delete_preference(cls, name: str) -> None:
        """
        Delete a preference from the database
        """
        preference = session.query(SavedPreference).filter_by(name=name).first()
        if preference:
            preference.delete()

    @classmethod
    def delete_preference_by_id(cls, preference_id: str) -> None:
        """
        Delete a preference from the database by id
        """
        preference = session.query(SavedPreference).filter_by(id=preference_id).first()
        if preference:
            preference.delete()
