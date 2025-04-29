import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, Request, Depends, Form, Query
from starlette.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")


def create_template(request: Request, var: dict):
    template = templates.get_template("websocket.tmpl")

    # 3. Рендерим в строку (если нужно дополнительно обработать)
    html_content = template.render(var=var)
    # 4. Возвращаем как HTMLResponse
    return html_content


@app.get("/auth/")
async def get(request: Request,):
    content=create_template(request=request,var={})
    return HTMLResponse(content=content)

@app.websocket("/auth/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")

if __name__ == "__main__":
    uvicorn.run("websocket:app", host="0.0.0.0", port=8020, reload=True)
