from agno.playground import Playground, serve_playground_app
from src.workflow.bi import BIWorkflow

from src.agents.python import python_agent

bi_workflow = BIWorkflow(
    name="数据分析工作流",
    workflow_id="bi_workflow",
)

app = Playground(agents=[python_agent], workflows=[bi_workflow]).get_app()

if __name__ == "__main__":
    serve_playground_app("src.playground.playground:app", reload=True)
