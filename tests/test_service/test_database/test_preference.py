from services.database.preference import PreferenceService
from storage.core.models import SavedPreference, Category


def test_create_preference(db_session):
    PreferenceService.create_preference(
        name="Test Preference",
        module_name="Test Module",
        preferences=["Test Category"],
    )
    preferences = db_session.query(SavedPreference).all()
    assert len(preferences) == 1
    assert preferences[0].name == "Test Preference"
    assert preferences[0].module_name == "Test Module"
    assert preferences[0].preferences[0].name == "Test Category"


def test_get_preference(db_session):
    preference = SavedPreference(
        name="Test Preference",
        module_name="Test Module",
        preferences=[Category(name="Test Category")],
    )
    preference.save()
    preference = PreferenceService.get_preference("Test Preference")
    assert preference.name == "Test Preference"
    assert preference.module_name == "Test Module"
    assert preference.preferences[0].name == "Test Category"


def test_get_preferences(db_session):
    preferences = PreferenceService.get_preferences()
    assert len(preferences) == 0

    preference = SavedPreference(
        name="Test Preference",
        module_name="Test Module",
    )
    preference.save()
    preference.preferences.append(Category(name="Test Category"))
    preference.save()
    preferences = PreferenceService.get_preferences()
    assert len(preferences) == 1
    assert preferences[0].name == "Test Preference"
    assert preferences[0].module_name == "Test Module"
    assert preferences[0].preferences[0].name == "Test Category"


def test_get_or_create_category(db_session):
    category = PreferenceService.get_or_create_category("Test Category")
    categories = db_session.query(Category).all()
    assert len(categories) == 1
    assert categories[0].name == category.name


# TODO: fix session mocking
# def test_add_category_to_preference(db_session):
#     preference = PreferenceService.create_preference(
#         name="Test Preference",
#         module_name="Test Module",
#         preferences=["Test Category"],
#     )
#     PreferenceService.add_category_to_preference(preference.id, "New Category")
#     preferences = PreferenceService.get_preferences()
#     assert len(preferences) == 1
#     assert preferences[0].name == "Test Preference"
#     assert preferences[0].module_name == "Test Module"
#     assert preferences[0].preferences[0].name == "Test Category"
#     assert preferences[0].preferences[1].name == "New Category"
