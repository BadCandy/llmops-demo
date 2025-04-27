from typing import Any, Dict
from libs.evaluators import Evaluator

from langchain.evaluation import load_evaluator, EvaluatorType
from langchain_core.runnables.base import Runnable
from langchain_core.embeddings import Embeddings


class EmbeddingDistanceEvaluator(Evaluator):

    def __init__(self, chain: Runnable, embedding_model: Embeddings):
        super().__init__(chain)
        self.embedding_model = embedding_model

    def evaluate(self, input_variables: dict, reference_output: str) -> Dict[str, Any]:
        result = super().evaluate(input_variables, reference_output)
        result["score"] = round(float(self.calculate_embedding_distance(result["output"], reference_output)), 2)
        return result

    def calculate_embedding_distance(self, output: str, reference_output: str) -> float:
        evaluator = load_evaluator(evaluator=EvaluatorType.EMBEDDING_DISTANCE, embeddings=self.embedding_model)
        return evaluator.evaluate_strings(prediction=output, reference=reference_output)["score"]
