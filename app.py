import os
import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceInstructEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from htmlTemplate import css, bot_template, user_template
from langchain.llms import HuggingFaceHub
from WebBot.Bot.Bot import AutoBot
import WebBot.Bot.Bot as bot
import WebBot.webai as aibot
import WebData.Links as link

def center_img(img_url):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(' ')
    with col2:
        st.image(img_url)
    with col3:
        st.write(' ')

def get_lists(string):
    string = str.lower(string)
    state_list = [" "]
    search_list = []
    question_list = []
    title_list = []

    if string == "states":
        states = open(link.states, "r")
        for state in states:
            state_list.append(state.replace("\n", ""))
        return state_list
    elif string == "search":
        search_terms = open(link.search_terms, "r")
        for search in search_terms:
            search_list.append(search.replace("\n", ""))
        return search_list
    elif string == "questions":
        questions = open(link.prompts, "r")
        for question in questions:
            question_list.append(question.strip())
        return question_list
    elif string == "titles":
        titles = open(link.titles, "r")
        for title in titles:
            title_list.append(title.replace("\n", ""))
        return title_list
    else:
        st.write("Enter a valid list!")

def get_txt():
    text = ""
    with open(link.results, "r", encoding='utf-8') as saved_file:
        text = saved_file.read()
        saved_file.close()
    return text

def load_web_data(selected_state, selected_city):
    search_list = get_lists("Search")
    raw_text = get_txt()
    if len(raw_text) != 0:
        if st.button("Clear Data"):
                bot.clear_results(link.results)
    else:
        if st.button("Load Webpage"):
            with st.spinner("Gathering data..."):
                aibot.Automation(selected_state, selected_city, search_list)
                raw_text = get_txt()
    return raw_text

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text        

def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

def get_vectorstore(text_chunks):
    # embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-xl")
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    return vectorstore

def get_conversation_chain(vectorstore):
    llm = ChatOpenAI()
    # llm = HuggingFaceHub(repo_id="google/flan-t5.xxl", model_kwargs={"temperature":0.5, "max_length":512})
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    conversation_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        memory=memory 
    )
    return conversation_chain

def handle_userinput(user_question, ask_question):
    response = st.session_state.conversation({"question": user_question})
    st.session_state.chat_history = response['chat_history']

    with open(link.landscape_doc, 'a', encoding='utf-8') as saved_content:
        for i, message in enumerate(st.session_state.chat_history):
            if ask_question:
                if i % 2 == 0:
                    st.write(user_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)
                else:
                    st.write(bot_template.replace("{{MSG}}", message.content), unsafe_allow_html=True)
            
        saved_content.write(f'{message.content} \n')
        saved_content.close()

def train_model(raw_text):
    if st.button("Train Model"):
        with st.spinner("Training AI model..."):

            text_chunks = get_text_chunks(raw_text)
        
            vectorstore = get_vectorstore(text_chunks)

            st.session_state.conversation = get_conversation_chain(vectorstore)


def main():

    load_dotenv()
    st.set_page_config(page_title="Mustafa's Bot 🤖", page_icon="\U0001F916")
    st.write(css, unsafe_allow_html=True)

    cities_list = [" "]
    pdf_docs = [] 
    raw_text = " "
    lot_size = 500

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None
    
    # st.header("🤖 Archiwiz AI 🤖")
    # st.image("C:/Users/Archiwiz1/Pictures/a1.png")
    st.markdown("<h1 style='text-align: center; color: white;'>🤖 ⒶⒾWIZ🤖</h1>", unsafe_allow_html=True)
    
    ask_question = st.checkbox("Ask Question")
    try: 
        if ask_question:
            user_question = st.text_input(" Ask any question about the provided data:")
            if user_question:
                handle_userinput(user_question, ask_question)
        
        else:
            col1, col2 = st.columns(2)
            with col1:
                question_list = get_lists("Questions")
                title_list = get_lists("Titles")

                if st.button("Generate Landscaping Document"):
                    with st.spinner("Generating Document..."):
                        for i in range(len(question_list)):
                            with open(link.landscape_doc, 'a', encoding='utf-8') as saved_content:
                                saved_content.write(f'\n\n{title_list[i]}\n')
                                saved_content.close()
                            handle_userinput(f'In short {question_list[i].replace("lot_size", str(lot_size))}', ask_question)

            with col2:    
                if st.button("Clear Landscaping Document"):
                    bot.clear_results(link.landscape_doc)
    except:
        st.write("Please select the dataset!")

    #st.write(user_template.replace("{{MSG}}", "Hey! Bot"), unsafe_allow_html=True)
    #st.write(bot_template.replace("{{MSG}}", "Hi! Human"), unsafe_allow_html=True)
    
    
    with st.sidebar:
        #st.image("https://archiwiz.com/wp-content/uploads/2023/03/Logo.webp", width=275)
        center_img("https://archiwiz.com/wp-content/uploads/2023/03/Logo.webp")
        
        st.subheader("Dataset: :memo:")

        slider = st.select_slider('Pick the dataset:', ['Webpage Data', 'Select Files', 'Upload Files'])

        if slider == 'Webpage Data':
            
            if st.checkbox("Developer Mode"):
                selected_state = "Florida"
                selected_city = "Pinellas County"
                lot_size = 5000
                st.write(f"{selected_state} | {selected_city} | {lot_size}sqft")
                raw_text = load_web_data(selected_state, selected_city)
                train_model(raw_text)
                
                
            else:
                state_list = get_lists("States")
                selected_state = st.selectbox('State', state_list)

                if selected_state != " ":
                    cities = open(f'USA/{str(int(state_list.index(selected_state)) - 1)}.txt' , 'r')

                    for city in cities:
                        cities_list.append(city.replace("\n", ""))
                
                    selected_city = st.selectbox("City/County", cities_list)
                    
                    if selected_city != " ":
                        lot_size = st.number_input("Size of lot (sqft):", 0, 50_000, step = 500)

                        raw_text = load_web_data(selected_state, selected_city)
                        train_model(raw_text)
                    

        elif slider == 'Select Files':
            selected_pdfs = st.multiselect('Select Files', ['Landscaping', 'Setback Area', 'Shrubs', 'Tree types', 'Undesired plants', 'Vegetation'])
            pdf_docs = []

            if 'Landscaping' in selected_pdfs:
                pdf_docs.append("C:/Users/Archiwiz1/Desktop/AI Docs/Trees.pdf")
                pdf_docs.append("C:/Users/Archiwiz1/Desktop/AI Docs/Landscaping.pdf")
            if 'Setback Area' in selected_pdfs:
                pdf_docs.append("C:/Users/Archiwiz1/Desktop/AI Docs/setback area.pdf")
            if 'Shrubs' in selected_pdfs:
                pdf_docs.append("C:/Users/Archiwiz1/Desktop/AI Docs/Shrubs.pdf")
            if 'Tree types' in selected_pdfs:
                pdf_docs.append("C:/Users/Archiwiz1/Desktop/AI Docs/Native.pdf")    
                pdf_docs.append("C:/Users/Archiwiz1/Desktop/AI Docs/exotic.pdf")
                pdf_docs.append("C:/Users/Archiwiz1/Desktop/AI Docs/Palms.pdf")
            if 'Undisired plants' in selected_pdfs:
                pdf_docs.append("C:/Users/Archiwiz1/Desktop/AI Docs/undesired plants.pdf")
            if 'Vegetation' in selected_pdfs:
                pdf_docs.append("C:/Users/Archiwiz1/Desktop/AI Docs/Vegetation.pdf")
            with st.spinner("Uploading data..."):
                raw_text = get_pdf_text(pdf_docs)
                train_model(raw_text)
            

        elif slider == 'Upload Files':
            pdf_docs = st.file_uploader(":books: Upload PDFs here :books:", accept_multiple_files=True)
            with st.spinner("Uploading data..."):    
                raw_text = get_pdf_text(pdf_docs)
                train_model(raw_text)    
            

if __name__ == "__main__":
    main()
