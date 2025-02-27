from __future__ import annotations

import json
import os

from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from loguru import logger
from pydantic import BaseModel, Field

from src.feature_flags import flags


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


class IngredientList:
    _extract_instructions = """
        You will be given a context as a markdown file that has text extracted from a recipe website that contains the recipe, the ingredients and the number of servings.

        Read the whole context and find every ingredient in the recipe, the name of the recipe and the number of servings. Ensure that you find all the ingredients!

        Context: {context}
    """

    def __init__(self, model_name: str = "gpt-4o-mini"):
        self.model_name = model_name
        base_llm = ChatOpenAI(model=model_name, max_retries=3)
        self.llm = base_llm.with_structured_output(Recipe)

    async def process_content(self, content: str) -> Recipe | None:
        logger.info("Extracting recipe.")
        if flags.extract:
            recipe = await self.llm.ainvoke(
                [
                    SystemMessage(
                        content=IngredientList._extract_instructions.format(
                            context=content
                        )
                    )
                ],
            )

            if not recipe or not isinstance(recipe, Recipe) or not recipe.ingredients:
                logger.error("Could not process recipe")
                return None
            if flags.save:
                recipe.serialize(filename="data/recipe.json")
        else:
            recipe = Recipe.deserialize(filename="data/recipe.json")

        return recipe
