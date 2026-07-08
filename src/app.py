## ***************************************
import streamlit as st
from openai import OpenAI, api_key
from groq import Groq
from google import genai
# from app import answer, output, response_data
from core.config import config

def run_llm(provider, model_name, messages, max_tokens=500):
    if provider =="OpenAI":
     client=OpenAI(api_key=config.OPENAI_API_KEY)
    elif provider== "Groq":
     client=Groq(api_key=config.GROQ_API_KEY)
    else:
     client=genai.Client(api_key=config.GOOGLE_API_KEY)

    if provider == "Google":
     return client.models.generate_content(model=model_name, 
        contents=[message["content"] for message in messages]).text
    elif provider == "Groq":
      return client.chat.completions.create(model=model_name,
        messages=messages,
        max_completion_tokens=max_tokens,
        ).choices[0].message.content
    else:
     return client.chat.completions.create(
        model=model_name,
        messages=messages,
        max_completion_tokens=max_tokens,
        reasoning_effort="minimal"
        ).choices[0].message.content

# streamlet application to diplay dropdown model list and the providers

# def run_llm(provider, model_name, messages, max_tokens=500):
#     if provider == "OpenAI":
#         client = OpenAI(api_key=config.OPENAI_API_KEY)
#     elif provider == "Groq":
#         client = Groq(api_key=config.GROQ_API_KEY)
#     else:
#         client = genai.Client(api_key=config.GOOGLE_API_KEY)

#     if provider == "Google":
#         return client.models.generate_content(model=model_name, 
#             contents=[message["content"] for message in messages]).text
#     elif provider == "Groq":
#         return client.chat.completions.create(
#             model=model_name,
#             messages=messages,
#             max_completion_tokens=max_tokens,
#         ).choices[0].message.content
#     else:
#         return client.chat.completions.create(
#             model=model_name,
#             messages=messages,
#             max_completion_tokens=max_tokens,
#         ).choices[0].message.content

# def main():
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
    st.markdown(prompt)
    with st.chat_message("user"):
        st.chat_message(prompt)

    with st.chat_message("assistant"):
        output=run_llm(st.session_state.provider, st.session_state.model_name, st.session_state.messages)
        # response_data= output
        # answer=response_data
        st.write(output)
    st.session_state.messages.append({"role": "assistant", "content": output})

# if __name__ == "__main__":
#     main()


# ******************* Cleanup version with main function
# import streamlit as st
# from openai import OpenAI
# from groq import Groq
# from google import genai
# from core.config import config

# def run_llm(provider, model_name, messages, max_tokens=500):
#     if provider == "OpenAI":
#         client = OpenAI(api_key=config.OPENAI_API_KEY)
#     elif provider == "Groq":
#         client = Groq(api_key=config.GROQ_API_KEY)
#     else:
#         client = genai.Client(api_key=config.GOOGLE_API_KEY)

#     if provider == "Google":
#         return client.models.generate_content(model=model_name, 
#             contents=[message["content"] for message in messages]).text
#     elif provider == "Groq":
#         return client.chat.completions.create(
#             model=model_name,
#             messages=messages,
#             max_completion_tokens=max_tokens,
#         ).choices[0].message.content
#     else:
#         return client.chat.completions.create(
#             model=model_name,
#             messages=messages,
#             max_completion_tokens=max_tokens,
#         ).choices[0].message.content

# def main():
#     with st.sidebar:
#         st.title("Settings")
        
#         # Dropdown for provider
#         provider = st.selectbox("Provider", ["OpenAI", "Groq", "Google"])
#         if provider == "OpenAI":
#             model_name = st.selectbox("Model", ["gpt-4o-mini", "gpt-4o"])
#         elif provider == "Groq":
#             model_name = st.selectbox("Model", ["llama-3.3-70b-versatile"])
#         else:
#             model_name = st.selectbox("Model", ["gemini-2.5-flash"])
        
#         # Save model and provider to session state
#         st.session_state.provider = provider
#         st.session_state.model_name = model_name

#     # Initialize chat messages
#     if "messages" not in st.session_state:
#         st.session_state.messages = [{"role": "assistant", "content": "Hello! How can I assist you today?"}]
    
#     # Display chat history
#     for message in st.session_state.messages:
#         with st.chat_message(message["role"]):
#             st.markdown(message["content"])

#     # Chat input
#     if prompt := st.chat_input("Type your message..."):
#         st.session_state.messages.append({"role": "user", "content": prompt})
#         with st.chat_message("user"):
#             st.markdown(prompt)

#         with st.chat_message("assistant"):
#             output = run_llm(st.session_state.provider, st.session_state.model_name, st.session_state.messages)
#             st.write(output)
#             st.session_state.messages.append({"role": "assistant", "content": output})

# if __name__ == "__main__":
#     main()