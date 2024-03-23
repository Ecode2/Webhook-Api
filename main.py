from fastapi import Body, Depends, FastAPI, Path, Query, Request, Response, HTTPException, status
from fastapi.security import APIKeyQuery,  SecurityScopes
from db.engine.db import Base, engine, get_db
from db.models import models
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from db.schemas.customers import create_customer, get_customer, get_customer_by_id, update_user_info
from db.schemas.schemas import CustomerBase, CustomerCheck, CustomerResponse, CustomerApiResponse, CustomerUpdate
import requests
from dotenv import load_dotenv


API_VERSION = "v0.1.0"

app = FastAPI(
    title="Reastaurant API",
    description="An API for restaurants built with FastAPI",
    version=API_VERSION,
    docs_url=f"/",
    redoc_url=f"/api/{API_VERSION}/redoc",
    swagger_ui_oauth2_redirect_url= "/oauth2-redirect"
)

load_dotenv()

app.add_middleware(
  CORSMiddleware,
  allow_origins = ["*"],
  allow_credentials = True,
  allow_methods = ["*"],
  allow_headers = ['*']
)

# Create database tables
models.Base.metadata.create_all(engine)
#models.create_db()


# Define dependencies
def confirm_ip_address(request: Request):

    allowed_ip = ["52.31.139.75",
                "52.49.173.169",
                "52.214.14.220"]

    client_ip = request.client.host

    if client_ip not in allowed_ip:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorised to access this page"
        )

    return {"client_ip": client_ip}

def confirm_api_key(request: Request, db: Session = Depends(get_db) ):
    try:
        
        apiKey = request.query_params.get("apiKey")

        if not apiKey:
            raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorised to access this page"
            )

        user = db.query(models.Customer).filter(models.Customer.id == apiKey).first()
        

        if not user:
            raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorised to access this page"
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorised to access this page"
            )

def get_request_class(request: Request) -> Request:

    return request.base_url


@app.post("/signup", response_model=CustomerApiResponse, summary="Create a unique user_id for webhooks")
async def Create_WebHook_Url(request: Request, Body: CustomerBase = Body(None), current_url = Depends(get_request_class), db: Session = Depends(get_db)):

    customer_info = await create_customer(db=db, request=Body)

    schema_info = CustomerResponse( **customer_info.__dict__)

    return  {"user_data": schema_info,
             "webhook_url": f"{current_url}/webhook/url/{schema_info.id}"
             }


@app.post("/user", response_model=CustomerApiResponse, summary="retrieve all information about a user")
async def Get_User_Info(request: Request, Body: CustomerCheck = Body(None), current_url = Depends(get_request_class), db: Session = Depends(get_db)):

    customer_info = await get_customer(db=db, request=Body) 

    schema_info = CustomerResponse( **customer_info.__dict__)

    return  {"user_data": schema_info,
             "webhook_url": f"{current_url}/webhook/url/{schema_info.id}"
             }



@app.put("/user/update/",  summary="Update account details")
async def Update_User_Info( email: str = Query(None), password: str = Query(None), Body: CustomerUpdate = Body(None), db: Session = Depends(get_db)):

    if not password or not email or not Body:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing a parameter"
            )
    print("before update")
    await update_user_info(db=db, email=email, password=password, body=Body) 
    print("after update")

    return  {"message": "Account Information Updated"}, 200



@app.post("/webhook/url/{user_id}", summary="handle webhook events from paystack", status_code=200)
async def handle_webhook(user_id: str , request = Body(None), confirm_ip =  Depends(confirm_ip_address), db: Session = Depends(get_db) ):

    customer_info = await get_customer_by_id(db=db, user_id=user_id) 

    schema_info = CustomerBase( **customer_info.__dict__)

    if schema_info.url and not schema_info.database:
        print("wow", request)
        try:
            response = requests.post(
                url= str(schema_info.url),
                headers= {
                    "Content-Type": "application/json"
                },
                json = request
            )

            return {'Status': 'success', "Status_code": response.status_code}, 200
            

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Webhook did not respond. error: {e}"
                )
    
    elif schema_info.url and schema_info.database:
        try:
            response = requests.post(
                url= str(schema_info.url),
                headers= {
                    "Content-Type": "application/json"
                },
                json = request
            )

            # TODO: send information to database server

            return {'Status': 'success', "Status_code": response.status_code}, 200
            

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Webhook did not respond. error: {e}"
                )
    
    elif not schema_info.url and schema_info.database:
        """ try:
            response = requests.post(
                url= str(schema_info.url),
                headers= {
                    "Content-Type": "application/json"
                },
                json = request
            )

            return {'Status': 'success', "Status_code": response.status_code}, 200
            

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Webhook did not respond. error: {e}"
                ) """
        # TODO: send information to database server
        pass

    elif not schema_info.url and not schema_info.database:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User doesn't have a webhook url or database"
                )

    return {
              'Status': 'success',
              'data': "successfully handled"
          }, 200
