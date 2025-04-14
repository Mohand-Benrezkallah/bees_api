import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from strawberry.fastapi import GraphQLRouter

from app.core.config import settings
from app.schema import schema, get_context

# Create the FastAPI application
app = FastAPI(title=settings.PROJECT_NAME)

# Create GraphQL router with our schema
graphql_app = GraphQLRouter(
    schema,
    context_getter=get_context,
    graphiql=True  # Enable GraphiQL web interface
)

# Add GraphQL endpoint
app.include_router(graphql_app, prefix="/graphql")

# Configure static file serving for bee images
# Ensure the directory exists
os.makedirs(settings.STATIC_FILES_DIR, exist_ok=True)
app.mount("/images", StaticFiles(directory=settings.STATIC_FILES_DIR), name="images")

@app.get("/")
async def root():
    """Root endpoint that provides API information and redirects to GraphQL UI"""
    return {
        "message": "Bee API",
        "version": "1.0.0",
        "graphql_endpoint": "/graphql",
    }