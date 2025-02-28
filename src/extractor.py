from __future__ import annotations

import json
import os

from dotenv import load_dotenv
from loguru import logger
from pydantic import BaseModel, Field
from pydantic_ai import Agent, ModelRetry

from src.feature_flags import flags

if not flags.use_docker:
    assert load_dotenv()


class Ingredient(BaseModel):
    name: str = Field(description="The name of the ingredient")
    quantity: float = Field(
        description="The quantity of the ingredient. Leave empty if not applicable eg when ingredient just says chopped cilantro"
    )
    unit: str = Field(
        description="The unit of the ingredient like tbsp, cup, etc. Leave empty if not applicable. eg leave this empty if the ingredient is somthing like 3 cloves or 4 eggs etc"
    )
    notes: str = Field(
        description="Any additional notes about the ingredient, eg chopped, minced, substitutes etc. Leave empty if not applicable. Don't start with 'Note:'"
    )


class Recipe(BaseModel):
    name: str = Field(description="The name of the recipe")
    servings: int = Field(description="The number of servings the recipe makes")
    ingredients: list[Ingredient]

    def serialize(self, filename: str = "data/recipe.json"):
        dir_path = os.path.dirname(filename)
        os.makedirs(dir_path, exist_ok=True)
        with open(filename, "w") as f:
            json.dump(self.model_dump(), f, indent=2)

    @staticmethod
    def deserialize(filename: str = "data/recipe.json") -> Recipe:
        with open(filename, "r") as f:
            data = json.load(f)
        recipe = Recipe.model_validate(data)
        return recipe

    def __str__(self) -> str:
        s = ""
        s += f"Name: {self.name}\n"
        s += f"Servings: {self.servings}\n"
        s += "Ingredients:\n"
        for i, ingredient in enumerate(self.ingredients):
            s += f"{i + 1}. {ingredient.name} - {ingredient.quantity} {ingredient.unit} : {ingredient.notes}\n"
        return s


class RecipeContent(BaseModel):
    markdown: str = Field(description="Recipe in markdown format")


extractor_agent = Agent(
    "gpt-4o-mini",
    result_type=Recipe,
    retries=3,
    system_prompt="""
        You will be given a markdown file content that has text extracted from a recipe website that contains the recipe, the ingredients and the number of servings.

        Read the whole content and find every ingredient in the recipe, the name of the recipe and the number of servings. Ensure that you find all the ingredients!
    """,
)


@extractor_agent.result_validator
def validate_result(recipe: Recipe | None) -> Recipe:
    if not recipe or not recipe.ingredients:
        logger.error(f"Failed to extract recipe: {recipe}")
        raise ModelRetry("Failed to extract recipe")
    return recipe
