
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.gzip import GZipMiddleware

app = FastAPI()

# 添加會話中間件
app.add_middleware(SessionMiddleware, secret_key="your_secret_key")
app.mount("/static", StaticFiles(directory="static"))
templates = Jinja2Templates(directory="templates")


# 假設帳號和密碼存儲在數據庫中
fake_username = "test"
fake_password = "test"

@app.post("/signin")
async def login(request: Request, username: str = Form(None), password: str = Form(None)):
    print("Received username:", username)
    print("Received password:", password)
    print("Expected username:", fake_username)
    print("Expected password:", fake_password)
    if not username or not password:
        request.session["SIGNED_IN"] = False
        print("Username or password not provided")
        return RedirectResponse(url="/error?message=請輸入帳號和密碼", status_code=303)
    elif (username == fake_username) and (password == fake_password):
        request.session["SIGNED_IN"] = True
        print("User signed in successfully")
        return RedirectResponse(url="/member", status_code=303)
    else:
        request.session["SIGNED_IN"] = False
        print("Username or password incorrect")
        return RedirectResponse(url="/error?message=帳號或密碼錯誤", status_code=303)


# Success page（用戶如果沒有登入，返回主頁) (用戶如果按下返回鍵，就無法再登入)
@app.get("/member", response_class=HTMLResponse)
async def member_page(request: Request):
    if request.session.get("SIGNED_IN"):
        # Add cache control headers only for the member page
        response = templates.TemplateResponse("success.html", {"request": request,})
        response.headers["Cache-Control"] = "no-store"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    else:
       return RedirectResponse(url="/")
    

# Logout endpoint
@app.get("/signout")
async def signout(request: Request):
    request.session["SIGNED_IN"] = False
    return RedirectResponse(url="/", status_code=303)

# Error page endpoint
@app.get("/error", response_class=HTMLResponse)
async def error_page(request: Request, message: str):
    return templates.TemplateResponse("failure.html", {"request": request, "message": message})


# Login page (uses GET method)
@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    # If user is already signed in, redirect to success page
    if request.session.get("SIGNED_IN"):
        return RedirectResponse(url="/success")
    return templates.TemplateResponse("index.html", {"request": request})

# 當你使用狀態碼303進行重定向時，客戶端（例如瀏覽器）會遵循HTTP規範，
# 使用GET方法來重新請求指定的URL，從而顯示了頁面內容。而如果不指定狀態碼，或者使用其他狀態碼（如默認的302重定向），
# 則客戶端可能會根據自己的策略來處理重定向，可能會使用之前的請求方法，這樣可能導致405錯誤。
# 因此，使用狀態碼303確保了客戶端在重定向時使用GET方法，這符合了你的路由定義，從而可以正確地顯示頁面內容。

# 1. 使用者登入正確，成功頁面
# 2. 使用者登入失敗，成功頁面
# 3. 使用者沒有填寫帳號、密碼，直接送出，失敗頁面（請輸入正確的帳號密碼），送回主頁
# 4. 使用者登入後，按下返回鍵，無法再回來/member 頁面

