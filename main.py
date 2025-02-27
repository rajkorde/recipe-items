import asyncio
from typing import Annotated

import typer
from dotenv import load_dotenv

from src.extractor import IngredientList
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
    url = "https://natashaskitchen.com/chicken-stir-fry-recipe/"

    content = scrape_and_convert_to_md(url)
    if not content:
        typer.echo("Could not scrape website")
        raise typer.Exit(1)
    recipe = asyncio.run(IngredientList().process_content(content))
    if not recipe:
        typer.echo("Could not extract recipe")
        raise typer.Exit(1)
    print(recipe)


if __name__ == "__main__":
    app()
