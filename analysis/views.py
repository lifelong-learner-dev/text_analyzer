import environ
from django.http import JsonResponse
from langchain import OpenAI
from langchain.chains import ConversationChain
from django.views.decorators.csrf import csrf_exempt
import json
import openai
import time

# 환경 변수 로드
env = environ.Env()
environ.Env.read_env()

# OpenAI API 키 설정
openai_api_key = env('OPENAI_API_KEY')
openai_api_key2 = env('OPENAI_ASSISTANTS_API_KEY')


# 첫 번째 LLM (conversation_chain)
llm1 = OpenAI(api_key=openai_api_key)
conversation_chain1 = ConversationChain(llm=llm1)

# 두 번째 LLM (conversation_chain2)
llm2 = OpenAI(api_key=openai_api_key2)
conversation_chain2 = ConversationChain(llm=llm2)
# 대화 기록 저장을 위한 리스트
conversation_history = []

@csrf_exempt
def continue_conversation(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # JSON 본문 데이터 처리
            user_input = data.get('text')

            # LangChain을 통해 대화를 이어나감
            conversation_response = conversation_chain1.invoke({"input": user_input})
            
            # 대화 내용을 저장
            conversation_history.append(conversation_response)
            
            return JsonResponse({
                'conversation': conversation_response,
            })
        except Exception as e:
            print(f"Error during conversation: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def analyze_text(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # JSON 본문 데이터 처리
            analysis_input = data.get('analysis_input')  # 감정 분석 및 요약 요청

            # 대화 기록을 하나의 텍스트로 결합
            conversation_context = "\n".join(
                [f"User: {item['input']}\nAI: {item['response']}" for item in conversation_history]
            )

            # 분석 요청을 위한 프롬프트 생성
            prompt = f"The following is a conversation history:\n{conversation_context}\n\nThe user requested the following analysis:\n{analysis_input}\n\nPlease provide the analysis of conversations in the conversation history."

            # 두 번째 LLM을 사용하여 감정 분석 및 요약 요청
            response = conversation_chain2.run(prompt)

            return JsonResponse({'result': response.strip()})
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)