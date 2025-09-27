"""Services for seller operations."""

import datetime
import random
from typing import Optional, List, Dict
from fastapi import HTTPException, status
from app.models.seller import Seller, Language, Experience, Education
from app.schemas.seller import SellerCreate, SellerUpdate
from app.core.exceptions import DocumentNotFound, UserAlreadyExists
from app.core.logger import logger
from beanie import PydanticObjectId

class SellerService:
    """Service class for seller operations."""

    @staticmethod
    async def get_seller_by_id(seller_id: str) -> Optional[Dict]:
        """Get seller by ID."""
        seller = await Seller.get(seller_id)
        if not seller:
            raise DocumentNotFound("Seller with the specified ID not found.")
        return seller.model_dump()

    @staticmethod
    async def get_seller_by_username(username: str) -> Optional[Dict]:
        """Get seller by username."""
        seller = await Seller.get_by_username(username)
        if not seller:
            raise DocumentNotFound("Seller with the specified ID not found.")
        return seller.model_dump()

    @staticmethod
    async def get_seller_by_email(email: str) -> Optional[Dict]:
        """Get seller by email."""
        seller = await Seller.get_by_email(email)
        if not seller:
            raise DocumentNotFound("Seller with the specified ID not found.")
        return seller.model_dump()

    @staticmethod
    async def create_seller(seller_data: SellerCreate) -> Optional[Dict]:
        """Create a new seller profile."""
        # Check if seller already exists
        existing_seller = await Seller.get_by_email(seller_data.email)
        if existing_seller:
            raise UserAlreadyExists("Seller with the specified email already exists.")
        seller = Seller(**seller_data.model_dump(by_alias=True))
        await seller.insert()
        logger.info(f"Created new seller with ID: {seller.model_dump()}")
        return seller.model_dump()


    @staticmethod
    async def update_seller(seller_id: str, seller_data: SellerUpdate) -> Optional[Dict]:
        """Update seller profile."""
        seller = await Seller.get(seller_id)
        if not seller:
            raise DocumentNotFound("Seller with the specified ID not found.")

        # Update only provided fields
        update_data = seller_data.model_dump(exclude_unset=True, by_alias=True)
        for field, value in update_data.items():
            setattr(seller, field, value)

        await seller.save()
        logger.info(f"seller with id {seller_id} updated")
        return seller.model_dump()
    
    @staticmethod
    async def update_total_catalogs(seller_id: str, count: int) -> None:
        """Increment total_catalogs count."""
        logger.info(f"Update data recieved for {seller_id} with {count}")
        result = await Seller.find_one(Seller.id == PydanticObjectId(seller_id)).update(
            {"$inc": {"total_catalogs": count}}
        )
        if result.modified_count == 0:
            logger.warning(f"No seller updated for total_catalogs with ID {seller_id}")
        else:
            logger.info("seller info is updated")
        

    @staticmethod
    async def update_ongoing_jobs(seller_id: str, ongoing_jobs: int) -> None:
        """Increment ongoing_jobs."""
        result = await Seller.find_one(Seller.id == PydanticObjectId(seller_id)).update(
            {"$inc": {"ongoing_jobs": ongoing_jobs}}
        )
        if result.modified_count == 0:
            logger.warning(f"No seller updated for ongoing_jobs with ID {seller_id}")

    @staticmethod
    async def update_cancelled_jobs(seller_id: str) -> None:
        """Decrement ongoing_jobs and increment cancelled_jobs."""
        result = await Seller.find_one(Seller.id == PydanticObjectId(seller_id)).update(
            {"$inc": {"ongoing_jobs": -1, "cancelled_jobs": 1}}
        )
        if result.modified_count == 0:
            logger.warning(f"No seller updated for cancelled_jobs with ID {seller_id}")

    @staticmethod
    async def update_completed_jobs(data: Dict) -> None:
        """
        Update completed jobs for a seller.
        Expected data: {
            "seller_id": str,
            "ongoing_jobs": int,
            "completed_jobs": int,
            "total_earnings": float,
            "recent_delivery": str (ISO datetime)
        }
        """
        seller_id = data["seller_id"]
        result = await Seller.find_one(Seller.id == PydanticObjectId(seller_id)).update(
            {
                "$inc": {
                    "ongoing_jobs": data["ongoing_jobs"],
                    "completed_jobs": data["completed_jobs"],
                    "total_earnings": data["total_earnings"],
                },
                "$set": {"recent_delivery": datetime.fromisoformat(data["recent_delivery"])},
            }
        )
        if result.modified_count == 0:
            logger.warning(f"No seller updated for completed_jobs with ID {seller_id}")

    @staticmethod
    async def update_review(data: Dict) -> None:
        """
        Update review stats for a seller.
        Expected data: {
            "seller_id": str,
            "rating": int (1-5)
        }
        """
        rating_types = {
            "1": "one",
            "2": "two",
            "3": "three",
            "4": "four",
            "5": "five",
        }
        rating_key = rating_types[str(data["rating"])]
        seller_id = data["seller_id"]

        result = await Seller.find_one(Seller.id == PydanticObjectId(seller_id)).update(
            {
                "$inc": {
                    "ratings_count": 1,
                    "rating_sum": data["rating"],
                    f"rating_categories.{rating_key}.value": data["rating"],
                    f"rating_categories.{rating_key}.count": 1,
                }
            }
        )
        if result.modified_count == 0:
            logger.warning(f"No seller updated for review with ID {seller_id}")
            
    @staticmethod
    async def seed_sellers(count: int) -> List[Dict]:
        """Create random seller profiles for testing."""
        from faker import Faker
        fake = Faker()
        sellers = []

        for i in range(count):
            # Generate random seller data
            username = f"{fake.user_name()}_{i}"
            email = f"{fake.email()}_{i}"
            
            languages = [
                Language(language="English", level="Native"),
                Language(language=fake.random_element(elements=("Spanish", "French", "German", "Italian")), 
                        level=fake.random_element(elements=("Basic", "Conversational", "Fluent")))
            ]
            
            experience = [
                Experience(
                    company=fake.company(),
                    title=fake.job(),
                    start_date=fake.date_between(start_date="-5y", end_date="-2y").strftime("%Y-%m-%d"),
                    end_date=fake.date_between(start_date="-2y", end_date="today").strftime("%Y-%m-%d"),
                    description=fake.text(max_nb_chars=200),
                    currently_working_here=fake.boolean(chance_of_getting_true=30)
                )
            ]
            
            education = [
                Education(
                    country=fake.country(),
                    university=fake.company(),
                    title=fake.random_element(elements=("Bachelor's", "Master's", "PhD")),
                    major=fake.random_element(elements=("Computer Science", "Engineering", "Business", "Design")),
                    year=str(fake.year())
                )
            ]
            
            seller = Seller(
                full_name=fake.name(),
                username=username,
                email=email,
                profile_picture=fake.image_url(),
                description=fake.text(max_nb_chars=500),
                profile_public_id=fake.uuid4(),
                oneliner=fake.catch_phrase(),
                country=fake.country(),
                languages=languages,
                skills=fake.random_elements(
                    elements=("Python", "JavaScript", "React", "Node.js", "Django", "FastAPI", "MongoDB", "PostgreSQL"),
                    length=random.randint(3, 6),
                    unique=True
                ),
                experience=experience,
                education=education,
                social_links=[fake.url() for _ in range(2)]
            )
            
            await seller.save()
            sellers.append(seller.model_dump())
        return sellers


