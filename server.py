from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import PlainTextResponse,HTMLResponse,JSONResponse
from pydantic import BaseModel
from copy import deepcopy
from secrets import token_hex
from uvicorn import run
from time import time

Voucher={}
app=FastAPI()
indexS=open("index.html","r",encoding="utf8").read()

class RedeemP(BaseModel):
    mobile: str
    voucher_hash: str

app.mount("/campaign/src", StaticFiles(directory="src"), name="static")

@app.get("/",response_class=HTMLResponse)
def api_root():
    return "<html><head><title>503 Service Temporarily Unavailable</title></head><body><center><h1>503 Service Temporarily Unavailable</h1></center></body></html>"

@app.get("/createW",response_class=PlainTextResponse)
def api_createW(Money:float,Message:str=""):
    Id=token_hex(18)[:35]
    Voucher[Id]={
        "status":{"message":"success","code":"SUCCESS"}, # Voucher is expired. VOUCHER_EXPIRED / Voucher ticket is out of stock. VOUCHER_OUT_OF_STOCK
        "data":{
            "voucher": {
                "voucher_id":"696969696969696969",
                "amount_baht":"%.2f" % Money,
                "redeemed_amount_baht":"0.00",
                "member":1,
                "status":"active", # redeemed
                "link":Id,
                "detail":Message,
                "expire_date":(int(time())+172800)*1000, # 86400 = 1 day
                "redeemed":0,
                "available":1
            },
            "owner_profile":{"full_name":"larina x999"},
            # "redeemer_profile":None,
            # "my_ticket":None,
            "tickets":[]
        }
    }
    return f"https://YOUR.DOMAIN.COM/campaign/?v={Id}"

@app.get("/campaign/",response_class=HTMLResponse)
def api_index():return indexS

@app.get("/api/{ID}/verify")
def api_verify(ID:str,mobile:str=""):
    print(mobile[:10])
    if ID not in Voucher:return JSONResponse(content={"status":{"message":"Voucher doesn't exist.","code":"VOUCHER_NOT_FOUND"},"data":None},status_code=400)
    elif Voucher[ID]["status"]["code"] != "SUCCESS": return JSONResponse(content=Voucher[ID],status_code=400)
    resp=deepcopy(Voucher[ID])
    resp["data"]["redeemer_profile"]={"mobile_number":mobile[:10]}
    return JSONResponse(content=resp,status_code=200)


@app.post("/api/{ID}/redeem")
def api_redeem(ID:str,body: RedeemP):
    if ID not in Voucher:return JSONResponse(content={"status":{"message":"Voucher doesn't exist.","code":"VOUCHER_NOT_FOUND"},"data":None},status_code=400)
    phone=body.mobile[:10]
    now=int(time())*1000
    me=Voucher[ID]
    amount=me["data"]["voucher"]["amount_baht"]
    me["data"]["tickets"].append({"mobile":f"{phone[0:3]}-xxx-{phone[6:]}","update_date":now,"amount_baht":amount,"full_name":f"SomeOne {phone[6:]}"})
    me["data"]["voucher"]["redeemed_amount_baht"]=amount
    me["data"]["voucher"]["redeemed"]+=1
    me["data"]["voucher"]["available"]-=1
    resp=deepcopy(me)
    if me["data"]["voucher"]["available"] <= 0:
        me["status"]["message"]="Voucher ticket is out of stock."
        me["status"]["code"]="VOUCHER_OUT_OF_STOCK"
        me["data"]["voucher"]["status"]="redeemed"

    resp["data"]["redeemer_profile"]={"mobile_number":phone}
    resp["data"]["my_ticket"]={"mobile":phone,"update_date":now,"amount_baht":amount,"full_name":"อรรถพร การุญ"}
    return JSONResponse(content=resp,status_code=200)

@app.get("/api/deeplink")
def api_deeplink():
    return {"status":{"message":"success","code":"SUCCESS"},"data":"https://tmn.app.link/?deeplink=ascendmoney%3A%2F%2Fwallet.truemoney.co.th%2Fapp%2F660000000015"}

if __name__ == "__main__":run("server:app",host="127.0.0.1",port=999)
