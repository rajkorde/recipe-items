import marimo

__generated_with = "0.11.11"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
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
        scrape_and_convert_to_md,
    )


@app.cell
def _(mo):
    url_form = (
        mo.md(
            """
            {url}
            """
        )
        .batch(
            url=mo.ui.text(label="Recipe URL", full_width=True, value="https://twokooksinthekitchen.com/best-pad-thai-recipe/"),
        )
        .form(show_clear_button=True, bordered=False)
    )
    url_form
    return (url_form,)


@app.cell
def _(mo, url_form):
    status = mo.md(f"Scraping website: {url_form.value["url"]}") if url_form.value else mo.md("")
    status
    url_form.value
    return (status,)


@app.cell
def _(mo, scrape_and_convert_to_md, url):
    content = scrape_and_convert_to_md(url)
    if not content:
        status = mo.md("Could not scrape website")
        mo.stop()
    return content, status


@app.cell
def _(UnexpectedModelBehavior, content, extractor_agent, mo):
    try:
        result = extractor_agent.run_sync(f"Markdown:\n {content}")
    except UnexpectedModelBehavior:
        status = mo.md("Could not extract recipe")
        mo.stop()

    if not result or not result.data:
        mo.md("Could not extract recipe")
        mo.stop()
    recipe = result.data
    if not recipe or not recipe.ingredients:
        mo.md("Could not extract recipe")
        mo.stop()

    recipe.name
    recipe.servings
    return recipe, result, status


@app.cell
def _(mo, pd, recipe, url_form):
    def get_table(recipe):
        data = pd.DataFrame([i.model_dump() for i in recipe.ingredients])
        table = mo.ui.table(data)
        return table
    

    mo.md('') if not url_form.value or not url_form.value["url"] or not recipe else get_table(recipe)

    return (get_table,)


if __name__ == "__main__":
    app.run()
