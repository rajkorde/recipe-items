from typing import Annotated

import pandas as pd
import typer
from dotenv import load_dotenv
from loguru import logger
from pydantic_ai import UnexpectedModelBehavior
from rich.console import Console
from rich.table import Table
from rich.text import Text

from src.extractor import Recipe, extractor_agent
from src.feature_flags import flags
from src.scraper import scrape_and_convert_to_md

__version__ = "0.1.5"

app = typer.Typer(no_args_is_help=True, add_completion=False)
if not flags.use_docker:
    assert load_dotenv()


def version_callback(value: bool):
    if value:
        print(f"Recipe-Items  CLI Version: {__version__}")
        raise typer.Exit()


@app.command()
def generate(url: Annotated[str, typer.Option(help="Recipe URL", show_default=False)]):
    logger.info("Scraping website: " + url)
    content = scrape_and_convert_to_md(url)
    if not content:
        typer.echo("Could not scrape website")
        raise typer.Exit(1)

    logger.info("Extracting recipe.")
    if flags.extract:
        result = None
        try:
            result = extractor_agent.run_sync(f"Markdown:\n {content}")
        except UnexpectedModelBehavior:
            typer.echo("Could not extract recipe")
            raise typer.Exit(1)

        if not result or not result.data:
            typer.echo("Could not extract recipe")
            raise typer.Exit(1)
        recipe = result.data
        if not recipe or not recipe.ingredients:
            typer.echo("Could not extract recipe")
            raise typer.Exit(1)
        if flags.save:
            recipe.serialize(filename="data/recipe.json")
    else:
        recipe = Recipe.deserialize(filename="data/recipe.json")

    # typer.echo(str(recipe))

    df = pd.DataFrame([i.model_dump() for i in recipe.ingredients])
    console = Console()

    table = Table(title="Ingredients")
    for column in df.columns:
        table.add_column(column, justify="left")

    # Add rows dynamically from DataFrame values
    for row in df.itertuples(index=False):
        table.add_row(*map(str, row))

    console.print("\n\n")
    console.print(Text(f"{recipe.name}", style="bold underline cyan", justify="center"))
    console.print(
        Text(f"Servings: {recipe.servings}", style="italic cyan", justify="center")
    )
    console.print("")
    console.print(table)


if __name__ == "__main__":
    app()
