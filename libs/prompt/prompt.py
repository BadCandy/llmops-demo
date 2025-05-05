import sqlite3

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from libs.model.model_provider import ChatModelManager
from libs.util.secret import DEFAULT_DATABASE_PATH


class Prompt:
    def __init__(self, prompt_name: str, version_id: int = None, database: str = DEFAULT_DATABASE_PATH):

        self.conn = sqlite3.connect(database)
        self.prompt_name = prompt_name
        self.version_id = version_id if version_id else self._get_last_version()

        self.system_template, self.user_template = self._get_prompt_by_version()

    def _get_last_version(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT MAX(pv.version_id) AS version_id
                FROM prompt_versions pv
                JOIN prompts p ON pv.prompt_id = p.id
                WHERE p.prompt_name = ?
            ''', (self.prompt_name,))
            row = cursor.fetchone()
            if row:
                return row[0]
            else:
                return None
        except Exception as ex:
            print(f"Error fetching last version: {ex}")
            return None

    def _get_prompt_by_version(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT pv.system_template, pv.user_template
                FROM prompt_versions pv
                JOIN prompts p ON pv.prompt_id = p.id
                WHERE p.prompt_name = ? AND pv.version_id = ?;
            ''', (self.prompt_name, self.version_id))
            row = cursor.fetchone()
            if row:
                return row[0], row[1]  # system_template, user_template 반환
            else:
                return None, None  # 해당 조건에 맞는 데이터가 없을 경우
        except Exception as ex:
            print(f"Error fetching prompt by version: {ex}")
            return None, None

    def get_chat_template(self):
        return ChatPromptTemplate.from_messages([
            ("system", self.system_template),
            ("user", self.user_template)
        ])


if __name__ == '__main__':
    chat_prompt_template = Prompt(prompt_name="오늘의_날씨", version_id=3).get_chat_template()
    print(chat_prompt_template)

    chat_model_manager = ChatModelManager()
    model = chat_model_manager.get_model(
        model_name="mistral",
        **chat_model_manager.get_model_require_args(
            model_name="mistral",
        )
    )
    parser = StrOutputParser()
    chain = chat_prompt_template | model | parser
    res = chain.invoke(
        {"text": "안녕하세요. 오늘 날씨가 어때요?"}
    )
    print(res)
