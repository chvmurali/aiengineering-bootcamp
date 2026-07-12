import json
from pyexpat.errors import messages

from streamlit.runtime.state import SessionState
from app import message, model_name, provider
from chatbot_ui.core.config import config
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import logging 
from fastapi import BackgroundTasks
import requests
from streamlit import session_state, streamlit as st

def api_call(method, url, **kwargs):

    def _show_error_message(message):
        """Show error message as a popup on right corner"""
        st.session_state["error_popup"] = { "visible": True, "message": message, }
    try:
        response = getattr(requests, method)(url, **kwargs)
        try:
            response_data=response.json()
        except requests.exceptions.JSONDecodeError:
            response_data = {"message", "Invalid response format from server"}

        if response.ok:
            return True, response_data
        
            return False, response_data
    except requests.exceptions.ConnectionError:
        _show_error_message(" Connection error! Check your network connection")
        return False, {"message", "connection error"}
    except requests.exceptions.Timeout:
        _show_error_message(" Timeout error! Check your network connection")
        return False, {"message", "Request timeout"}
    except Exception as e :
        _show_error_message(" Unexcepted error occurred", {str(e)})
        return False, {"message", {str(e)}}


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class ChatRequest(BaseModel):
    provider: str
    model_name: str
    messages: list[dict]
    max_tokens: int = 500
    reasoning_effort: str = "minimal"

class ChatResponse(BaseModel):
    answer: str
app = FastAPI()

@app.get("/")
def root():
    return RedirectResponse(url="/docs")

@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:

  result = api_call( "post", f"{config.API_URL}/chat", json={"provider": st.session_state.provider,
   "model_name": st.session_state.model_name,
   "messages": st.SessionState.messages})
  return ChatResponse(answer=result)

@app.get("/health")
def health():
    return {"status": "ok"}
