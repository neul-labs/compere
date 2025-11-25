import click
import uvicorn


@click.command()
@click.option("--host", default="127.0.0.1", help="Host to bind the server to")
@click.option("--port", default=8090, help="Port to bind the server to")
@click.option("--reload", is_flag=True, help="Enable auto-reload on code changes")
def main(host, port, reload):
    """Compere CLI to run the web service."""
    uvicorn.run("compere.main:app", host=host, port=port, reload=reload)

if __name__ == "__main__":
    main()