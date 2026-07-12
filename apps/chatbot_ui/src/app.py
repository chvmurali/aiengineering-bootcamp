import json
from pyexpat.errors import messages

from streamlit.runtime.state import SessionState
# from app import message, model_name, provider
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

#lets craete a side bar with model list and providers selection
with st.sidebar:
    st.title("Settings")
    #dropdown for model
    provider=st.selectbox("Proivider", ["OpenAI", "Groq", "Google"])
    if provider == "OpenAI":
        model_name=st.selectbox("Model", ["gpt-5-nano", "gpt-5-mini"])
    elif provider== "Groq":
        model_name=st.selectbox("Model", ["llama-3.3-70b-versatile"])
    else:
        model_name=st.selectbox("Model", ["gemini-2.5-flash"])
    #Save model and the provider to the satate
    st.session_state.provider=provider
    st.session_state.model_name=model_name

if "messages" not in st.session_state:
    st.session_state.messages=[{"role": "assistant", "content": "Hello! How can I assist you today?"}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Hello! How can I assist you today?"):
    st.session_state.messages.append({"role": "user", "content":prompt})
    # st.markdown(prompt)
    with st.chat_message("user"):
        st.chat_message(prompt)

    with st.chat_message("assistant"):
        # output=run_llm(st.session_state.provider, st.session_state.model_name, st.session_state.messages)
        # # response_data= output
        # # answer=response_data
        # st.write(output)
        # payload={"provider": st.session_state.provider,
        #     "models_name": st.session_state.model_name,
        #     "messages": st.session_state.messages}

        payload = {"model": "llama-3.3-70b-versatile",
            "messages": [{"role": "system", "content": "You are a helpful assistant."},
                  {"role": "user", "content": "generate 5 random numbers!"}]}

        print ("Request: ",  payload, indent=2)
        output = api_call("post", f"{config.API_URL}/chat", json=payload)
        print("response data" ,  output)
        # response_data = output
        # answer = response_data["message"]
        # st.write(answer)
        st.write(output)
#   return ChatResponse(answer=result)
    st.session_state.messages.append({"role": "assistant", "content": answer})


# ************************

# class ChatRequest(BaseModel):
#     provider: str
#     model_name: str
#     messages: list[dict]
#     max_tokens: int = 500
#     reasoning_effort: str = "minimal"

# class ChatResponse(BaseModel):
#     answer: str
# app = FastAPI()

# @app.get("/")
# def root():
#     return RedirectResponse(url="/docs")

# @app.post("/chat", response_model=ChatResponse)

# def chat(payload: ChatRequest) -> ChatResponse:
#   output = api_call( "post", f"{config.API_URL}/chat", json={"provider": st.session_state.provider,
#    "model_name": st.session_state.model_name,
#    "messages": st.SessionState.messages})
#   response_data=output[1],
#   answer=response_data["message"],
#   st.write(answer)
# #   return ChatResponse(answer=result)
#   st.session_state.messages.append({"role": "assistant", "content": answer})

# @app.get("/health")
# def health():
#     return {"status": "ok"}
