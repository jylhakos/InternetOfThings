import asyncio
import os

from langchain.chat_models import init_chat_model
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from mcp import ClientSession
from mcp.client.sse import sse_client

base_url = os.getenv("OPENAI_API_BASE_URL")
model = os.getenv("MODEL_NAME")
mcp_server_url = os.getenv("MCP_SERVER_URL")
api_key = os.getenv("OPENAI_API_KEY", "does_not_matter")

system_prompt = """You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct {dialect} query to run,
then look at the results of the query and return the answer. Unless the user
specifies a specific number of examples they wish to obtain, always limit your
query to at most {top_k} results.

You can order the results by a relevant column to return the most interesting
examples in the database.

Never query for all the columns from a specific table, only ask for the
relevant columns given the question.

You have access to tools for interacting with the database. Only use the given
tools. Only use the information returned by the tools to construct your final
answer.

You MUST double check your query before executing it. If you get an error while
executing a query, rewrite the query and try again.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the
database.

If the question does not seem related to the database, just return "I don't
know" as the answer.

To list tables available - Use the following format to get a list of tables:
SELECT name FROM sqlite_master WHERE type='table';

To get the schema of a table - Use the PRAGMA statement like this:
PRAGMA table_info('your_table_name');
""".format(
    dialect=os.getenv("DATABASE_DIALECT"),
    top_k=5,
)


async def main():
    if mcp_server_url is None:
        raise ValueError("Please set the MCP_SERVER_URL environment variable.")

    llm = init_chat_model(
        model, model_provider="openai", api_key=api_key, base_url=base_url
    )

    async with sse_client(
        url=mcp_server_url,
        timeout=60,
    ) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await load_mcp_tools(session)
            print(f"MCP tools loaded: {tools}")

            agent = create_react_agent(
                llm,
                tools=tools,
                prompt=system_prompt,
            )

            question = os.getenv("QUESTION")
            if not question:
                raise ValueError(
                    "Please set the QUESTION environment variable with your question."
                )

            async for step in agent.astream(
                {"messages": [{"role": "user", "content": question}]},
                stream_mode="values",
            ):
                step["messages"][-1].pretty_print()


asyncio.run(main())
