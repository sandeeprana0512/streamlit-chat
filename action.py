from openai import OpenAI
import streamlit as st
from streamlit_js_eval import streamlit_js_eval

st.set_page_config(page_title="Streamlit Chat", page_icon="👍")
st.title("Debate")

if "setup_complete" not in st.session_state:
    st.session_state.setup_complete = False
if "user_message_count" not in st.session_state:
    st.session_state.user_message_count = 0
if "feedback_shown" not in st.session_state:
    st.session_state.feedback_shown = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_complete" not in st.session_state:
    st.session_state.chat_complete = False

def complete_setup():
    st.session_state.setup_complete = True

def show_feedback():
    st.session_state.feedback_shown = True

if not st.session_state.setup_complete:

    st.subheader('Debate Information', divider='rainbow')

    if "name" not in st.session_state:
        st.session_state["name"] = ""

    st.session_state["name"] = st.text_input(label = "Name", max_chars = 40, placeholder = "Enter your debate topic")

    st.subheader('Difficulty Level', divider = 'rainbow')

    if "level" not in st.session_state:
        st.session_state["level"] = "Easy"

    st.session_state["level"] = st.radio(
        "Choose level",
        key="visibility",
        options=["Easy", "Medium", "Hard"],
    )

    if st.button("Start Debate", on_click=complete_setup):
        st.write("Setup complete. Starting Debate...")

if st.session_state.setup_complete and not st.session_state.feedback_shown and not st.session_state.chat_complete:

    st.info(
        """
        Start by introducing the topic.
        """,
        icon = "🫰"
    )

    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-4o"

    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role":"system",
            "content": (f"You are an Debate Judge that evaluate an debate on the topic called {st.session_state["name"]}. You should evaluate it for the difficulty level {st.session_state["level"]}.")
        }]

    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if st.session_state.user_message_count < 5:
        if prompt := st.chat_input("Your answer.", max_chars = 1000):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            if st.session_state.user_message_count < 4:
                with st.chat_message("assistant"):
                    stream = client.chat.completions.create(
                        model = st.session_state["openai_model"],
                        messages=[
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.messages
                        ],
                        stream=True,
                    )
                    response = st.write_stream(stream)
                
                st.session_state.messages.append({"role": "assistant", "content": response})

            st.session_state.user_message_count += 1

    if st.session_state.user_message_count >= 5:
        st.session_state.chat_complete = True

if st.session_state.chat_complete and not st.session_state.feedback_shown:
    if st.button("Get Feedback", on_click=show_feedback):
        st.write("Fetching feedback...")

if st.session_state.feedback_shown:
    st.subheader("Feedback")

    conversation_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages])

    feedback_client = OpenAI(api_key=st.secret["OPENAI_API_KEY"])

    feedback_completion = feedback_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": """You are a helpful tool that provides feedback on a debate competition.
             Follow this format:
             Feedback: //Here you put your feedback
             Give only the feedback do not ask any additional questions."""},
            {"role": "user", "content": f"This is the debate you need to evaluate. Keep in mind that you are only a tool. And you shouldn't engage in conversation: {conversation_history}"}
        ]
    )

    st.write(feedback_completion.choices[0].message.content)

    if st.button("Restart Interview", type="primary"):
        streamlit_js_eval(js_expressions="parent.window.location.reload()")