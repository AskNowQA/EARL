import streamlit as st
import requests
import json

def process_query(nlquery):
    url = 'https://earl.skynet.coypu.org/processQuery'
    headers = {'Content-Type': 'application/json'}
    data = json.dumps({'nlquery': nlquery})
    
    response = requests.post(url, headers=headers, data=data)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {'error': f'Error {response.status_code}: {response.text}'}

# Streamlit UI
st.title("Entity Linker UI")
st.write("Enter a natural language query and get linked entities and relations.")

# Input field for query
nlquery = st.text_input("Enter your query:", "Who is the president of Russia?")

if st.button("Process Query"):
    result = process_query(nlquery)
    
    if 'error' in result:
        st.error(result['error'])
    else:
        st.subheader("Extracted Entities and Relations")
        
        if 'chunktext' in result:
            for item in result['chunktext']:
                st.write(f"**{item['class'].capitalize()}:** {item['chunk']}")
        
        st.subheader("Reranked Entity and Relation Links")
        
        if 'rerankedlists' in result:
            for key, values in result['rerankedlists'].items():
                st.write(f"### List {key}")
                for score, uri in values:
                    st.write(f"- [{uri}]({uri}) (Score: {score:.4f})")

