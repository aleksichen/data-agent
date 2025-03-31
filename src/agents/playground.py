from agno.playground import Playground, serve_playground_app

from src.agents.datacatalog import data_catalog
from src.agents.datavis import data_visual

app = Playground(agents=[data_catalog, data_visual]).get_app()

if __name__ == "__main__":
    serve_playground_app("src.agents.playground:app", reload=True)