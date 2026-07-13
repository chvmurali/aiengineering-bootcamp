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
import streamlit as st

def api_call(method, url, **kwargs):

    print(f"API call: {method.upper()} {url} with params: {kwargs}")


    def _show_error_message(message):
        """Show error message as a popup on right corner"""
        st.session_state["error_popup"] = { "visible": True, "message": message, }
    try:
        response = getattr(requests, method)(url, **kwargs)
        try:
            response_data = response.json()
        except Exception:
            response_data = {"message": "Invalid response format from server"}

        if response.ok:
            return True, response_data
        else:
            return False, response_data
    except requests.exceptions.ConnectionError:
        _show_error_message(" Connection error! Check your network connection")
        return False, {"message": "connection error"}
    except requests.exceptions.Timeout:
        _show_error_message(" Timeout error! Check your network connection")
        return False, {"message": "Request timeout"}
    except Exception as e :
        _show_error_message(f" Unexpected error occurred: {e}")
        return False, {"message": str(e)}


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

        # payload = { "provider":"Google", "model_name":"gemini-2.5-flash",
        #     "messages": [{"role":"assistant", "content":"generate 5 random numbers!"}]}

        payload = { "provider":st.session_state.provider, "model_name":st.session_state.model_name,
            "messages": st.session_state.messages }
        
        print("Request: ", payload)
        success, response = api_call("post", f"{config.API_URL}/chat", json=payload)
        print("response data", response)
        try:
            json_response = json.dumps(response, indent=4)
        except Exception:
            json_response = str(response)
        print("JSON Response: ", json_response)

        # Determine answer from response in a few common formats
        answer = "No message returned from API"
        # if not success:
        #     answer = response.get("message", answer) if isinstance(response, dict) else str(response)
        # else:
        #     if isinstance(response, dict):
        #         # OpenAI-like: {choices: [{message: {content: "..."}}]}
        #         choices = response.get("choices")
        #         if choices and isinstance(choices, list):
        #             first = choices[0]
        #             # support dict or object-like
        #             msg = None
        #             if isinstance(first, dict):
        #                 msg = first.get("message")
        #                 if isinstance(msg, dict):
        #                     answer = msg.get("content", answer)
        #                 else:
        #                     answer = str(msg) if msg is not None else answer
        #             else:
        #                 # fallback for objects with attributes
        #                 answer = getattr(first, "message", getattr(first, "text", answer))
        #         else:
        #             # simple {"message": "..."}
        #             answer = response.get("message", answer)
        #     else:
        #         # fallback for other types
        #         answer = str(response)

        # answer = response.get("message", answer)

        # response is returned from api_call as (success, data) originally unpacked
        response_json = response if isinstance(response, dict) else {}

        # 1. Check if the API returned an error structure
        if not success:
            # response may be a dict with a message
            msg = response_json.get("message") if isinstance(response_json, dict) else str(response)
            st.error(f" API Error: {msg}")
        elif "error" in response_json:
            error_info = response_json["error"]
            if isinstance(error_info, dict):
                error_msg = error_info.get("message", str(error_info))
            else:
                error_msg = str(error_info)
            st.error(f" API Error: {error_msg}")

        # 2. Check if the expected 'choices' key exists
        elif "choices" in response_json:
            choices = response_json.get("choices", [])
            if choices and isinstance(choices, list):
                first_choice = choices[0]
                if isinstance(first_choice, dict):
                    message = first_choice.get("message", {})
                    if isinstance(message, dict):
                        assistant_response = message.get("content", "No response")
                    else:
                        assistant_response = str(message)
                else:
                    assistant_response = str(first_choice)
            else:
                assistant_response = "No response"
            
            # Display in Streamlit
            with st.chat_message("assistant"):
                st.markdown(assistant_response)
        else:
            # Fallback if something completely unexpected happens
            st.error(f"{response_json}")

        # print("Answer: ", answer)
        # st.write(answer)

        st.session_state.messages.append({"role": "assistant", "content": response_json.get("message", "No response") if isinstance(response_json, dict) else str(response)})

        #   return ChatResponse(answer=result)
    # st.session_state.messages.append({"role": "assistant", "content": answer})


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
