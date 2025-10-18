from sqlalchemy import Column, Integer, String, ForeignKey, Text, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    code = Column(String, unique=True, nullable=False)
    parent_id = Column(Integer, ForeignKey('categories.id'), nullable=True)

    parent = relationship("Category", remote_side=[id], backref="children")
    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Integer)
    category_id = Column(Integer, ForeignKey('categories.id'))
    subcategory = Column(String)  # e.g. "ru", "tr", "pryamaya", "uglovaya"
    image1 = Column(String)
    image2 = Column(String)
    image3 = Column(String)
    image4 = Column(String)
    size = Column(String)
    country = Column(String)
    type_ = Column(String)  # прямая, угловая и др.

    category = relationship("Category", back_populates="products")


class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    name = Column(String)
    phone = Column(String)
    product_id = Column(Integer, ForeignKey('products.id'))
    comment = Column(Text)
    status = Column(String, default="Новая")
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    product = relationship("Product")
