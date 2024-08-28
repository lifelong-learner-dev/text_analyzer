import environ
from django.http import JsonResponse
from langchain import OpenAI
from langchain.chains import ConversationChain
from django.views.decorators.csrf import csrf_exempt

# 환경 변수 로드
env = environ.Env()
environ.Env.read_env()

# OpenAI API 키 설정
openai_api_key = env('OPENAI_API_KEY')

# LangChain 및 OpenAI 클라이언트 설정
llm = OpenAI(openai_api_key=openai_api_key)
conversation_chain = ConversationChain(llm=llm)

# 대화 기록 저장을 위한 리스트
conversation_history = []

@csrf_exempt
def continue_conversation(request):
    try:
        user_input = request.POST.get('text', '')

        # LangChain을 사용하여 대화 이어나가기
        conversation_response = conversation_chain.run(user_input)

        # 대화 기록에 추가
        conversation_history.append(f"사용자: {user_input}")
        conversation_history.append(f"AI: {conversation_response}")

        # 'conversation' 키에 대화 내용을 담아 반환
        return JsonResponse({"conversation": f"사용자: {user_input} \n AI: {conversation_response}"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@csrf_exempt
def analyze_text(request):
    try:
        analysis_input = request.POST.get('analysis_input', '')

        # 대화 기록을 하나의 텍스트로 결합
        conversation_context = "\n".join(conversation_history)

        # 분석 요청과 함께 대화 내용을 프롬프트로 전달
        prompt = f"다음은 사용자와 AI 간의 대화 내용입니다:\n{conversation_context}\n\n" \
                 f"이 대화를 바탕으로 다음 질문을 분석해주세요:\n{analysis_input}"

        # LangChain을 사용하여 분석 수행
        analysis_response = conversation_chain.run(prompt)

        return JsonResponse({"result": analysis_response})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
