from typing import Any
from fastapi import HTTPException, Request, status
from db.models.models import Customer
from .hash import Hash 
from sqlalchemy.orm.session import Session
from sqlalchemy import  update
from .schemas import CustomerBase, CustomerCheck, CustomerUpdate

async def create_customer(db: Session, request: CustomerBase):

    newCustomer = Customer(
        username = request.username,
        url = request.url,
        email = request.email,
        password = Hash.bcrypt(request.password),
        database = request.database
    )

    db.add(newCustomer)
    db.commit()
    db.refresh(newCustomer)

    return newCustomer

async def get_customer(db: Session, request: CustomerCheck) -> Customer:

    customer = db.query(Customer).filter_by(email=request.email).first()

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Signup to access this endpoint"
            )

    if not Hash.verify(customer.password, request.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email or password Incorrect"
            )
    
    
    return customer

async def get_customer_by_id(db: Session, user_id: str) -> Customer:

    customer = db.query(Customer).filter_by(id=user_id).first()

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User Doesn't exist"
            )
    
    
    return customer


# Update customer info

async def update_user_info(db: Session, password: str, email:str, body: CustomerUpdate):

    customer = db.query(Customer).filter_by(email=email).first()

    if not Hash.verify(customer.password, password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email or password Incorrect"
            )
    
    db.add(customer)

    to_update = [body.username, body.password, body.url, body.database, body.email]
    
    updateable = {
        "username": body.username,
        "password": body.password,
        "url": body.url,
        "database": body.database,
        "email": body.email
    }

    if body.username:
        customer.username = body.username
        db.commit()
        print("username updated")
    if body.password:
        customer.password = Hash.sha256(body.password)
        db.commit()
        print("password updated")
    if body.url:
        customer.url = body.url
        db.commit()
        print("url updated")
    if body.database:
        customer.database = body.database
        db.commit()
        print("database updated")
    if body.email:
        customer.email = body.email
        db.commit()
        print("email updated")
    

    """ for k, v in updateable.items():
        if v and k != "password":
            db.query(Customer).filter(Customer.email == body.email).update({k:v}, synchronize_session='evaluate' )
            db.commit()
            print(f"{k} updated")
        elif v and k == "password":
            db.query(Customer).filter(Customer.email == body.email).update({k: Hash.bcrypt(v) }, synchronize_session='evaluate' )
            db.commit()
            print(f"{k} updated") """


    if not body.username and body.email and body.password and body.url and body.database:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Make at least one change"
            )
