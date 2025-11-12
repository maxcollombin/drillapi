from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from settings_values import cantons
from src.services.security import verify_ip
import httpx, json

router = APIRouter()
templates = Jinja2Templates(directory="src/templates")


@router.get("/checker/", response_class=HTMLResponse, dependencies=[Depends(verify_ip)])
async def checker(request: Request):
    config = cantons.CANTONS["cantons_configurations"]
    results = []

    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        for canton, data in config.items():
            canton_results = {"canton": canton, "checks": []}
            for location in data["exampleLocation"]:
                url = f"/v1/drill-category/{location[0]}/{location[1]}"
                check = {"url": url, "success": False, "status": None, "content": None}
                try:
                    resp = await client.get(url, timeout=60.0)
                    check["status"] = resp.status_code

                    # Check request
                    if resp.status_code == 200:
                        # check request content to define if result is a real success as query might return 200 but empty result or error message as text

                        if resp.json()["status"] == "sucess":
                            check["success"] = True

                        check["content"] = json.dumps(resp.json(), indent=2)
                    else:
                        content = (
                            resp.json()
                            if resp.headers.get("content-type") == "application/json"
                            else resp.text
                        )
                        check["content"] = content
                except Exception as e:
                    check["error"] = str(e)

                canton_results["checks"].append(check)

            results.append(canton_results)

    return templates.TemplateResponse(
        "checker.html",
        {
            "request": request,
            "results": results,
        },
    )
