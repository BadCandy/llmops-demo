import time
from enum import Enum
from typing import Any, Dict

from langchain_core.embeddings import Embeddings
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.base import Runnable

from libs.model.model_provider import ChatModelManager


class EvaluatorType(Enum):
    EXACT_MATCH = "ExactMatchEvaluator"
    EMBEDDING_DISTANCE = "EmbeddingDistanceEvaluator"
    LLM_JUDGE = "LLMJudgeEvaluator"


class Evaluator:
    def __init__(self, chain: Runnable):
        self.chain = chain

    def evaluate(self, input_variables: dict, reference_output: str) -> Dict[str, Any]:
        start_time = time.time()
        response = self.chain.invoke(input_variables)
        latency = time.time() - start_time

        evaluation_result = {
            "input_variables": input_variables,
            "output": response.content,
            "reference_output": reference_output,
            "input_token": response.usage_metadata["input_tokens"],
            "output_token": response.usage_metadata["output_tokens"],
            "latency": latency,
        }

        return evaluation_result


def create_evaluator(
        evaluator_type: EvaluatorType,
        chain: Runnable,
        judge_model: BaseChatModel = None,
        embedding_model: Embeddings = None,
) -> Evaluator:
    if evaluator_type == EvaluatorType.EXACT_MATCH:
        from libs.evaluator import ExactMatchEvaluator
        return ExactMatchEvaluator(chain=chain)
    elif evaluator_type == EvaluatorType.EMBEDDING_DISTANCE:
        if embedding_model is None:
            raise ValueError("embedding_model function must be provided for EmbeddingDistanceEvaluator")
        from libs.evaluator import EmbeddingDistanceEvaluator
        return EmbeddingDistanceEvaluator(chain=chain, embedding_model=embedding_model)
    elif evaluator_type == EvaluatorType.LLM_JUDGE:
        if judge_model is None:
            raise ValueError("judge_model function must be provided for LLMJudgeEvaluator")
        from libs.evaluator import LLMJudgeEvaluator
        return LLMJudgeEvaluator(chain=chain, judge_model=judge_model)
    else:
        raise ValueError(f"Unsupported evaluator type: {evaluator_type}")


if __name__ == '__main__':
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "주어진 문장의 감정을 긍정, 부정, 중립으로만 분류합니다. 분류에 대한 추가 설명을 하지 않습니다."),
        ("user", "문장: {sentence}\n분류:")
    ])

    chat_model_manager = ChatModelManager()
    model = chat_model_manager.get_model(
        model_name="mistral",
        temperature=0.1,
        max_tokens=100,
        **chat_model_manager.get_model_require_args(
            model_name="mistral",
        )
    )

    chain = prompt_template | model

    input_variables = {"sentence": "오늘 날씨 참 좋다"}
    reference_output = "긍정"

    evaluator = create_evaluator(EvaluatorType.EXACT_MATCH, chain=chain)

    # 평가 실행
    result = evaluator.evaluate(input_variables=input_variables, reference_output=reference_output)
    print(result)
