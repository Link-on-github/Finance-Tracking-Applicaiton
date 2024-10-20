import streamlit as st
import os
import google.generativeai as genai

# Setting API key
genai.configure(api_key="AIzaSyB1E027AvutFZftck6C5AVRaj_IHVpLeyw")

# Loading the model
model=genai.GenerativeModel("gemini-pro") 
chat = model.start_chat(history=[])
def get_gemini_response(question):
    
    response=chat.send_message(question,stream=True)
    return response

# Initialising the Streamlit app
st.set_page_config(page_title="Q&A Demo")

st.header("Gemini LLM Application")

if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

input=st.text_input("Input: ",key="input")
submit=st.button("Ask the question")

# Asking the question and getting the response
if submit and input:
    response=get_gemini_response(input)
    st.session_state['chat_history'].append(("You", input))
    st.subheader("The Response is")
    for chunk in response:
        st.write(chunk.text)
        st.session_state['chat_history'].append(("Bot", chunk.text))
st.subheader("The Chat History is") 

# Loading chat history    
for role, text in st.session_state['chat_history']:
    st.write(f"{role}: {text}")
    



    
