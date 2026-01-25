from fastapi import FastAPI, UploadFile, File, Form, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/process")
async def process_csv(file: UploadFile = File(...),seats: int = Form(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files allowed")

    try:
        df = pd.read_csv(file.file)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid CSV file")

    major = ["aids", "cs", "civil", "mech", "e&tc"]

    minor = {
        "aids": ["e&tc", "civil", "mech"],
        "cs": ["e&tc", "civil", "mech"],
        "civil": ["aids", "cs", "e&tc", "mech"],
        "mech": ["aids", "cs", "e&tc", "civil"]
    }

    df = df.sort_values(by=["Backlog", "Percentage"],ascending=[True, False])
    df["Branch"] = df["Branch"].str.lower().str.strip().replace("entc", "e&tc")
    df["Choice1"] = df["Choice1"].str.lower().str.strip().replace("entc", "e&tc")
    df["Choice2"] = df["Choice2"].str.lower().str.strip().replace("entc", "e&tc")
    df["Choice3"] = df["Choice3"].str.lower().str.strip().replace("entc", "e&tc")
    df["Minor"] = None
    minor_seats = { branch: {m: seats for m in minors} for branch, minors in minor.items()}
    for branch in df["Branch"].str.lower().unique():
        branch_students = df[df["Branch"].str.lower() == branch]

        for idx, row in branch_students.iterrows():
            assigned = False

            for choice_col in ["Choice1", "Choice2", "Choice3"]:
                choice = str(row.get(choice_col)).lower()

                if choice in minor_seats[branch] and minor_seats[branch][choice] > 0:
                    df.at[idx, "Minor"] = choice
                    minor_seats[branch][choice] -= 1
                    assigned = True
                    break

            if not assigned:
                for m, count in minor_seats[branch].items():
                    if count > 0:
                        df.at[idx, "Minor"] = m
                        minor_seats[branch][m] -= 1
                        break

    final_df = df.sort_values(
        by=["Branch", "Backlog", "Percentage"],
        ascending=[True, True, False]).reset_index(drop=True)
    return JSONResponse(final_df.to_dict(orient="records"))
