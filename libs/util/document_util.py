def format_docs(docs):
    # langchain Document를 prompt에 전달할 문자열로 포맷팅
    return '\n\n'.join([d.page_content for d in docs])
