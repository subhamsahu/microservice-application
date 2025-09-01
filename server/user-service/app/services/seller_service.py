"""Services for seller operations."""

import random
from typing import Optional, List, Dict
from fastapi import HTTPException, status
from app.models.seller import Seller, Language, Experience, Education
from app.schemas.seller import SellerCreate, SellerUpdate
from app.core.exceptions import DocumentNotFound, UserAlreadyExists
from app.core.logger import logger

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
        await seller.save()
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
        return seller.model_dump()
            
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


