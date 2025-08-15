from services.database.bio import BioService
from storage.core.models import Bio


def test_create_bio(db_session):
    BioService.create_bio(
        name="Test Bio",
        bio="Test Bio",
    )
    bios = db_session.query(Bio).all()
    assert len(bios) == 1
    assert bios[0].name == "Test Bio"
    assert bios[0].bio == "Test Bio"


def test_get_bio(db_session):
    bio = Bio(
        name="Test Bio",
        bio="Test Bio",
    )
    bio.save()
    bio = BioService.get_bio("Test Bio")
    assert bio.name == "Test Bio"
    assert bio.bio == "Test Bio"
