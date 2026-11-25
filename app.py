import streamlit as st
import boto3
from botocore.exceptions import ClientError
import json
import os
from bedrock_utils import query_knowledge_base, generate_response, valid_prompt


# Streamlit UI
st.title("Bedrock Chat Application")

# Sidebar for configurations
st.sidebar.header("Configuration")
model_id = st.sidebar.selectbox("Select LLM Model", ["us.anthropic.claude-haiku-4-5-20251001-v1:0", "us.anthropic.claude-sonnet-4-5-20250929-v1:0"])
kb_id = st.sidebar.text_input("Knowledge Base ID", os.environ.get("KB_ID", "your-knowledge-base-id"))  # export KB_ID=<stack2 output>
temperature = st.sidebar.select_slider("Temperature", [i/10 for i in range(0,11)], 0.0)  # low by default: spec numbers must not be invented
top_p = st.sidebar.select_slider("Top_P", [i/1000 for i in range(0,1001)], 1)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("What would you like to know?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if valid_prompt(prompt, model_id):
        # Query Knowledge Base
        kb_results = query_knowledge_base(prompt, kb_id)
        
        # Prepare context from Knowledge Base results
        context = "\n".join([result['content']['text'] for result in kb_results])
        
        # Generate response using LLM
        full_prompt = f"Context: {context}\n\nUser: {prompt}\n\n"
        response = generate_response(full_prompt, model_id, temperature, top_p)

        # Show where the answer came from (S3 document + relevance score)
        best = {}                                                   # file name -> best relevance score
        for result in kb_results:
            uri = result.get('location', {}).get('s3Location', {}).get('uri', 'unknown source')
            name = uri.split('/')[-1]
            best[name] = max(best.get(name, 0.0), result.get('score') or 0.0)
        if best and response:
            response += "\n\n**Sources**\n" + "\n".join(f"- `{n}` (relevance {sc:.2f})" for n, sc in best.items())
    else:
        response = "I'm unable to answer this, please try again"
    
    # Display assistant response
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
