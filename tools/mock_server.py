import uvicorn
from fastapi import FastAPI

app = FastAPI(title="GitHeal Mock API Server")

# In-memory flag to toggle schema drift
state = {"drift": False}

@app.get("/api/data")
def get_data():
    if not state["drift"]:
        # Healthy payload matching knowledge/api_spec.json
        return {
            "user_id": "usr_99827",
            "full_name": "John Doe",
            "account_status": "active"
        }
    else:
        # Drifted payload (full_name -> display_name, account_status -> account_state)
        return {
            "user_id": "usr_99827",
            "display_name": "John Doe",
            "account_state": "active"
        }

@app.post("/toggle-drift")
def toggle_drift():
    state["drift"] = not state["drift"]
    return {"status": "ok", "drift": state["drift"]}

@app.get("/status")
def get_status():
    return {"drift": state["drift"]}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
