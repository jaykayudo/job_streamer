from storage.core.models import Bio
from typing import List
from storage.core.engine import session


class BioService:
    @classmethod
    def get_bios(cls) -> List[Bio]:
        """
        Get all bios from the database
        """
        return session.query(Bio).all()

    @classmethod
    def create_bio(cls, name: str, bio: str) -> Bio:
        """
        Create a bio in the database
        """
        bio = Bio(name=name, bio=bio)
        bio.save()
        # session.refresh(bio)
        return bio

    @classmethod
    def get_bio(cls, name: str) -> Bio | None:
        """
        Get a bio from the database by name
        """
        return session.query(Bio).filter_by(name=name).first()

    @classmethod
    def get_bio_by_id(cls, bio_id: str) -> Bio | None:
        """
        Get a bio from the database by id
        """
        return session.query(Bio).filter_by(id=bio_id).first()

    @classmethod
    def delete_bio(cls, name: str) -> None:
        """
        Delete a bio from the database
        """
        bio = session.query(Bio).filter_by(name=name).first()
        if bio:
            bio.delete()

    @classmethod
    def delete_bio_by_id(cls, bio_id: str) -> None:
        """
        Delete a bio from the database by id
        """
        bio = session.query(Bio).filter_by(id=bio_id).first()
        if bio:
            bio.delete()
