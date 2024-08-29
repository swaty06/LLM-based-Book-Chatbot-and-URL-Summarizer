import os
import streamlit as st
import pickle
import time
from langchain import OpenAI
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import UnstructuredURLLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from utils import apply_background,custom_navbar
from dotenv import load_dotenv
from st_pages import add_page_title
from pathlib import Path

root_path = Path(__file__).parent.parent
media_path = root_path.joinpath("media")

def app():

    # Load environment variables from .env file, particularly the OpenAI API key
    load_dotenv()
    vectorstore_openai = None

    
    # Streamlit app setup
    st.title("Book Search Tool 📚")
    
    # Apply the background image
    apply_background(image_path="./app/media/book4.jpg")
    
    # Sidebar content
    st.sidebar.title("Book Search Tool 📚")
    st.sidebar.write("Enter up to three URLs related to a book or article. Process the URLs to ask questions about the content.")
    
    # Custom CSS for smaller URL input fields in the sidebar
    st.sidebar.markdown(
        """
        <style>
        .stTextInput {
            max-width: 250px;  /* Limit the width of text input fields */
            padding: 5px;  /* Add some padding for better UX */
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Input URLs from the user in the sidebar
    urls = [
        st.sidebar.text_input(f"URL {i+1}", key=f"url_{i}", placeholder="Enter URL here") 
        for i in range(3)
    ]
    
  
    # Move the Process URLs button to the sidebar
    process_url_clicked = st.sidebar.button("Process URLs")
    
    # File path for storing the FAISS index
    file_path = "vector_index.pkl"
    
    # Placeholder for displaying status messages
    main_placeholder = st.empty()
    
    # Initialize OpenAI LLM with specific parameters
    llm = OpenAI(temperature=0.8, max_tokens=500)
    
    # Processing logic for URLs
    if process_url_clicked:
        # load data
        loader = UnstructuredURLLoader(urls=urls)
        main_placeholder.text("Data Loading...Started...✅✅✅")
        data = loader.load()
        # split data
        text_splitter = RecursiveCharacterTextSplitter(
            separators=['\n\n', '\n', '.', ','],
            chunk_size=1000
        )
        main_placeholder.text("Text Splitter...Started...✅✅✅")
        docs = text_splitter.split_documents(data)
        # create embeddings and save it to FAISS index
        embeddings = OpenAIEmbeddings()
        vectorstore_openai = FAISS.from_documents(docs, embeddings)
        main_placeholder.text("Embedding Vector Started Building...✅✅✅")
        time.sleep(2)
    
        # Save the FAISS index to a pickle file
        with open(file_path, "wb") as f:
            vectorstore_openai.save_local("vectorstore")
    
   
    
    # Text input for user query on the main page
    st.header("Ask a Question Related to the Links Provided")
    query = st.text_input("Enter your question: ")
    
    # Handling the query input and processing
    if query:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                vectorstore = FAISS.load_local("vectorstore", OpenAIEmbeddings())
                chain = RetrievalQAWithSourcesChain.from_llm(llm=llm, retriever=vectorstore.as_retriever())
                result = chain({"question": query})
                st.header("Answer")
                st.write(result["answer"])
    
                # Display sources, if available
                sources = result.get("sources", "")
                if sources:
                    st.subheader("Sources:")
                    sources_list = sources.split("\n")
                    for source in sources_list:
                        st.write(source)

custom_navbar()

add_page_title(layout="wide")
app()
