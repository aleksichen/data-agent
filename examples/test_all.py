

from src.graph.types import State
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


def test_agent(query):
  # 创建状态
  state = State(
      messages=[HumanMessage(content=query)],
      next="",
      full_plan="",
      deep_thinking_mode=False,
      search_before_planning=False,
      TEAM_MEMBERS=["coordinator", "planner", "supervisor", "researcher", "coder", "browser", "reporter"]
  )
  
  


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        user_query = " ".join(sys.argv[1:])
    else:
        user_query = input("Enter your query: ")
    
    print("\n=== User Query ===")
    print(user_query)
    test_agent(user_query)