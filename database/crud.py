from sqlalchemy.orm import Session
from database.db import SessionLocal
from database.models import Category, Product, Order

def get_categories(parent_id=None):
    with SessionLocal() as session:
        q = session.query(Category)
        if parent_id is None:
            q = q.filter(Category.parent_id.is_(None))
        else:
            q = q.filter(Category.parent_id == parent_id)
        return q.all()

def get_category_by_id(category_id: int):
    with SessionLocal() as session:
        return session.query(Category).filter(Category.id == category_id).first()

def get_category_by_code(code: str):
    with SessionLocal() as session:
        return session.query(Category).filter(Category.code == code).first()

def add_category(name: str, code: str, parent_id=None):
    with SessionLocal() as session:
        cat = Category(name=name, code=code, parent_id=parent_id)
        session.add(cat)
        session.commit()
        session.refresh(cat)
        return cat

def delete_category(category_id: int):
    with SessionLocal() as session:
        cat = session.query(Category).filter(Category.id == category_id).first()
        if cat:
            session.delete(cat)
            session.commit()
            return True
        return False

def get_products_by_category(category_id: int, subcategory: str = None):
    with SessionLocal() as session:
        q = session.query(Product).filter(Product.category_id == category_id)
        if subcategory:
            q = q.filter(Product.subcategory == subcategory)
        return q.all()

def get_product(product_id: int):
    with SessionLocal() as session:
        return session.query(Product).filter(Product.id == product_id).first()

def get_all_products():
    with SessionLocal() as session:
        return session.query(Product).all()

def add_product(title: str, category_id: int, subcategory: str, country: str, type_: str,
                price: int, images: list, description: str, size: str):
    with SessionLocal() as session:
        p = Product(
            title=title,
            category_id=category_id,
            subcategory=subcategory,
            country=country,
            type_=type_,
            price=price,
            image1=images[0] if len(images) > 0 else None,
            image2=images[1] if len(images) > 1 else None,
            image3=images[2] if len(images) > 2 else None,
            image4=images[3] if len(images) > 3 else None,
            description=description,
            size=size
        )
        session.add(p)
        session.commit()
        session.refresh(p)
        return p

def update_product(product_id: int, **kwargs):
    with SessionLocal() as session:
        p = session.query(Product).filter(Product.id == product_id).first()
        if not p:
            return None
        for key, value in kwargs.items():
            setattr(p, key, value)
        session.commit()
        session.refresh(p)
        return p

def delete_product(product_id: int):
    with SessionLocal() as session:
        p = session.query(Product).filter(Product.id == product_id).first()
        if p:
            session.delete(p)
            session.commit()
            return True
        return False

def create_order(user_id: int, name: str, phone: str, product_id: int, comment: str):
    with SessionLocal() as session:
        o = Order(
            user_id=user_id,
            name=name,
            phone=phone,
            product_id=product_id,
            comment=comment,
            status="Новая"
        )
        session.add(o)
        session.commit()
        session.refresh(o)
        return o

def get_orders(status: str = None):
    with SessionLocal() as session:
        q = session.query(Order)
        if status:
            q = q.filter(Order.status == status)
        return q.order_by(Order.created_at.desc()).all()

def get_order(order_id: int):
    with SessionLocal() as session:
        return session.query(Order).filter(Order.id == order_id).first()

def update_order_status(order_id: int, status: str):
    with SessionLocal() as session:
        o = session.query(Order).filter(Order.id == order_id).first()
        if o:
            o.status = status
            session.commit()
            session.refresh(o)
        return o
