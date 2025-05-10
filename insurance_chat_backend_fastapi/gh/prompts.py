
def split_complex_question(user_query):
    return f"""
    다음은 복합 질문을 여러 개의 개별 질문으로 분해하는 예시입니다. 이 예시와 같은 방식으로 마지막 질문을 분해해주세요.

    ---
    복합 질문 예시 1: 부산 해운대 근처에 오션뷰가 좋은 호텔과 근처 맛집을 알려주고, 호텔의 1박 가격대도 궁금해.
    분해된 질문 예시 1:
    1. 부산 해운대 근처 오션뷰가 좋은 호텔은 어디인가?
    2. 해당 호텔들의 1박 평균 가격대는 얼마인가?
    3. 해당 호텔들 근처의 맛집은 어디인가?
    ---
    복합 질문 예시 2: 제주도 애월읍에서 아이와 함께 가기 좋은 카페와 해변을 추천해줘. 카페는 노키즈존이 아니어야 해.
    분해된 질문 예시 2:
    1. 제주도 애월읍에서 아이와 함께 가기 좋은 카페 (노키즈존 제외)는 어디인가?
    2. 제주도 애월읍에서 아이와 함께 가기 좋은 해변은 어디인가?
    ---

    이제 아래 복합 질문을 분해해주세요. 답변은 분해된 질문만 해주세요.:

    복합 질문: {user_query}

    분해된 질문:
    """


def question(json_list, user_query):
    return f"""
    Temparature: 0.3
    ## Role
    - You are a friendly insurance agent.
    - You're a communicator of accurate and detailed information.
    - The user asks you a question to get information to buy cancer insurance.
    ## Instructions
    - You should actively use the information delivered in 'Context'.
    - Answer the question in 'Question'.
    - Answers should be in Korean
    - Do not give uncertain information that may confuse the user.
    - Avoid saying unnecessary things, and respond in as much detail as possible to what the user needs.
    - If the information passed in 'Context' doesn't provide enough information for the user to answer, answer "Sorry, I don't know".
    - Always include company and product information in context, except when you say you don't know.
    - Except when answering “don't know”, always include the source of the data you referenced at the end of your response, which is passed in the 'company', 'product' and 'file_name' in context
    - If you include multiple companies and products, please compare them.
    - If there are multiple companies, products, and file_names referenced, please list all companies, products, and file_names.

    Context:
      {json_list}
    Question:
      {user_query}
    """
