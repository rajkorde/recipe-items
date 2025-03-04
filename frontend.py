import marimo

__generated_with = "0.11.11"
app = marimo.App(width="medium", app_title="Recipe Items")


@app.cell
def _():
    import marimo as mo
    import nest_asyncio
    import pandas as pd
    from dotenv import load_dotenv
    from loguru import logger
    from pydantic_ai import UnexpectedModelBehavior

    from src.extractor import Recipe, extractor_agent
    from src.feature_flags import flags
    from src.scraper import scrape_and_convert_to_md
    return (
        Recipe,
        UnexpectedModelBehavior,
        extractor_agent,
        flags,
        load_dotenv,
        logger,
        mo,
        nest_asyncio,
        pd,
        scrape_and_convert_to_md,
    )


@app.cell
def _(flags, load_dotenv, nest_asyncio):
    nest_asyncio.apply()
    if not flags.use_docker:
        assert load_dotenv()
    return


@app.cell
def _(mo):
    url_form = (
        mo.md(
            """
            {url}
            """
        )
        .batch(
            url=mo.ui.text(
                label="Recipe URL",
                full_width=True,
                value="https://twokooksinthekitchen.com/best-pad-thai-recipe/",
            ),
        )
        .form(show_clear_button=False, bordered=False)
    )
    url_form
    return (url_form,)


@app.cell
async def _(
    Recipe,
    UnexpectedModelBehavior,
    extractor_agent,
    flags,
    mo,
    scrape_and_convert_to_md,
    url_form,
):
    import asyncio

    if url_form.value:
        error = ""
        with mo.status.spinner(title=f"Scraping recipe url...") as _spinner:
            url = url_form.value["url"]
            content = ""
            try:
                content = scrape_and_convert_to_md(url)
            except Exception as e:
                error = f"Scraping failed with: {str(e)}"
            if not content:
                error = "Could not scrape website."
                _spinner.update("Could not scrape website.")

            _spinner.update("Extracting Ingredients...")
            if flags.extract:
                result = None
                try:
                    result = extractor_agent.run_sync(f"Markdown:\n {content}")
                except UnexpectedModelBehavior:
                    error = f"Could not extract recipe: {str(UnexpectedModelBehavior)}"

                if not result or not result.data:
                    error = "Could not extract recipe"

                recipe = result.data
                if not recipe or not recipe.ingredients:
                    error = "Could not extract recipe"

                if flags.save:
                    recipe.serialize(filename="data/recipe.json")
            else:
                recipe = Recipe.deserialize(filename="data/recipe.json")

            await asyncio.sleep(1)
            _spinner.update("Done")
    return asyncio, content, error, recipe, result, url


@app.cell
def _(error, mo, pd, recipe, url_form):
    def get_table(recipe):
        data = pd.DataFrame([i.model_dump() for i in recipe.ingredients])
        table = mo.ui.table(
            data,
            pagination=False,
            show_column_summaries=False,
            label="### Ingredients",
        )
        return table

    results = None

    if url_form.value:
        if error:
            results = mo.md(f"<span style='color:red'>**Error:** {error}</span>")
        else:
            title = mo.md(f"#{recipe.name}")
            servings = mo.md(f"##Servings: {recipe.servings}")
            item_table = get_table(recipe)
            results = mo.vstack([title, servings, item_table])

    results
    return get_table, item_table, results, servings, title


if __name__ == "__main__":
    app.run()
