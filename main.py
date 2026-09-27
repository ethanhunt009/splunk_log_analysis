import time
from warnings import filterwarnings
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
from langchain.agents import initialize_agent, AgentType

import agent

load_dotenv()
filterwarnings("ignore")


# ---------- Tools ----------
tool_list = [
    agent.splunk_csv_load_tool,
    agent.splunk_log_read,
    agent.report_anomaly_tool,
    agent.report_error_tool,
    agent.update_suricata_rule_tool,
]


# ---------- LLMs ----------
def init_gemini():
    return ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.1)


def init_claude():
    return ChatAnthropic(model="claude-3-5-sonnet-20240620", temperature=0)


# ---------- MongoDB chat history ----------
CONNECTION_STRING = "mongodb://localhost:27017"
DATABASE_NAME = "chat"
COLLECTION_NAME = "chat_history"
SESSION_ID = "session_1"

chat_history = MongoDBChatMessageHistory(
    connection_string=CONNECTION_STRING,
    database_name=DATABASE_NAME,
    collection_name=COLLECTION_NAME,
    session_id=SESSION_ID,
    create_index=True,
)


# ---------- Agents ----------
gemini_agent = initialize_agent(
    tools=tool_list,
    llm=init_gemini(),
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True,
)

anthropic_agent = initialize_agent(
    tools=tool_list,
    llm=init_claude(),
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True,
)


# ---------- Call helper ----------
def call_gemini(query: str) -> str:
    """Call the Gemini agent with a user query."""
    try:
        return gemini_agent.run(query)
    except KeyboardInterrupt:
        raise
    except Exception as e:
        return f"An error occurred: {e}"


# ---------- Main chat loop ----------
def chat():
    print("Type 'exit' to quit.\n")
    try:
        while True:
            start = time.time()
            user_input = input("Enter your query: ").strip()

            if user_input.lower() == "exit":
                print("Goodbye.")
                break
            if not user_input:
                continue

            # Persist user message
            chat_history.add_user_message(user_input)

            # Run the agent with the actual user input
            response = call_gemini(user_input)

            # Persist AI response
            chat_history.add_ai_message(str(response))

            print(f"\nResponse: {response}")
            print(f"Time taken: {time.time() - start:.2f}s\n")

    except KeyboardInterrupt:
        print("\nYou have exited.")


if __name__ == "__main__":
    chat()