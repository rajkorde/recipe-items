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
            url=mo.ui.text(label="Recipe URL", full_width=True),
        )
        .form(show_clear_button=True, bordered=False)
    )
    url_form
    return (url_form,)


@app.cell
def _(mo):
    # Create a form with multiple elements
    form = (
        mo.md(
            """
            **Your form.**

            {name}

            {date}
            """
        )
        .batch(
            name=mo.ui.text(label="name"),
            date=mo.ui.date(label="date"),
        )
        .form(show_clear_button=True, bordered=True)
    )
    form
    return (form,)


@app.cell
def _(form):
    form.value
    return


@app.cell
def _(form, mo, pd):
    def get_table(form):
        data = pd.DataFrame([[form.value["name"],form.value["date"]]], columns=["Name", "DOB"])
        table = mo.ui.table(data)
        return table
    

    mo.md('') if not form.value or not form.value["name"] else get_table(form)

    return (get_table,)


if __name__ == "__main__":
    app.run()
