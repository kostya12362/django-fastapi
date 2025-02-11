from fastapi import FastAPI


def custom_openapi(app: FastAPI):
    openapi_schema = app.openapi()
    for path, detail in openapi_schema["paths"].items():
        for method in detail.values():
            if not method.get("parameters"):
                continue
            for parameter in method["parameters"]:
                if parameter["schema"].get("type") == "array":
                    parameter |= {"explode": False, "style": "form"}
    app.openapi_schema = openapi_schema
    return app
