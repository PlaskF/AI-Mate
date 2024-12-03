from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import pymysql
import requests
from openai import OpenAI
import base64

# 마리아DB 주소
try:
    con = pymysql.connect(host="eco-align.c5iieq4w2nsc.ap-northeast-2.rds.amazonaws.com",
                          user="root",
                          password="12341234",
                          port=3306,
                          db='eco-align',
                          charset='utf8')
except pymysql.MySQLError as e:
    print(f"데이터베이스 연결 오류: {e}")
    con = None

# 기상예보 api 키 설정
weather_api_key = "your-api-key-here"

# OpenAI API 키 설정
try:
    client = OpenAI(api_key="your-api-key-here")
    assistant = client.beta.assistants.retrieve(assistant_id='your-assistant_id-here')
    thread = client.beta.threads.create()
except Exception as e:
    print("OpenAI API 설정 오류")
    client = None


# 기상정보 API 함수
def get_current_weather(**kwargs):
    city = kwargs['city']

    # API endpoint
    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city,
        'appid': weather_api_key,
        'units': 'metric',
        'lang': 'kr'
    }

    # API를 호출하여 데이터 가져오기
    try:
        # API를 호출하여 데이터 가져오기
        response = requests.get(url, params=params)
        response.raise_for_status()  # HTTP 오류 발생 시 예외 처리
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"기상 API 호출 중 오류가 발생했습니다: {e}"}), 502  # Bad Gateway

    try:
        # 응답을 JSON 형태로 변환
        data = response.json()
        # 필요한 정보 추출
        weather_description = data['weather'][0]['description']
        temperature = data["main"]["temp"]
        temp_min = data["main"]["temp_min"]
        temp_max = data["main"]["temp_max"]
        feels_like = data["main"]["feels_like"]
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
    except (KeyError, TypeError, ValueError) as e:
        return jsonify({"error": f"응답 데이터 처리 중 오류가 발생했습니다: {e}"}), 500  # Internal Server Error

    return temperature, weather_description, temp_min, temp_max, feels_like, humidity, wind_speed


# DB SQL 작성 함수
def ask_schedule(**kwargs):
    if con is None:
        return jsonify({"error": "데이터베이스 연결이 설정되지 않았습니다."}), 500

    # --------------------------------------------------------------------------------------------
    # 토큰에서 ID 추출하기
    # 헤더에서 'Authorization' 값을 가져옵니다.
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({'error': 'Authorization header is missing'}), 401

    # 'Bearer ' 부분을 제거합니다.
    token = auth_header.split(' ')[1]

    # JWT는 'Header.Payload.Signature' 형태이므로 Payload 부분을 디코딩합니다.
    payload = token.split('.')[1]

    # Base64 디코딩
    # Base64 패딩 문제를 해결하기 위해 문자열 길이를 4의 배수로 조정합니다.
    payload += '=' * (-len(payload) % 4)
    decoded_payload = base64.urlsafe_b64decode(payload).decode('utf-8')

    # JSON 포맷으로 파싱
    decoded_json = json.loads(decoded_payload)

    # 'sub' 필드에 저장된 ID 내용을 텍스트로 반환
    sub_value = decoded_json.get('sub', 'No subject provided')
    # --------------------------------------------------------------------------------------------

    cursor = con.cursor()
    user_query = kwargs['query']
    query_type = user_query.strip().upper().split()[0]  # 쿼리의 첫 단어로 타입 판별 (INSERT, SELECT 등)

    # query = f"{user_query} AND member_id = '{sub_value}';"

    # INSERT일 경우 member_id를 VALUES에 추가
    if query_type == 'INSERT':
        # 공백으로 쿼리의 각 단어를 나누고, 'VALUES' 키워드를 찾기
        query_parts = user_query.split()

        # 'VALUES' 이전 부분에 `member_id` 추가
        if 'VALUES' in query_parts:
            values_index = query_parts.index('VALUES')  # 'VALUES' 키워드의 위치 찾기

            # INSERT 구문에 `member_id`를 추가
            columns_part = ' '.join(query_parts[:values_index])  # 'VALUES' 이전의 컬럼 부분
            values_part = ' '.join(query_parts[values_index:])  # 'VALUES' 이후의 값 부분

            # ')' 전에 `member_id`를 추가하고, VALUES의 값에도 `sub_value` 추가
            columns_part = columns_part.rstrip(')') + ', member_id)'
            values_part = values_part.rstrip(')') + f", '{sub_value}')"

            query = f"{columns_part} {values_part}"
        else:
            # 'VALUES' 키워드가 없는 경우 처리 (다른 쿼리인 경우)
            query = user_query
    else:
        # SELECT, UPDATE, DELETE일 경우에는 AND 조건 추가
        query = f"{user_query} AND member_id = '{sub_value}';"
    if not query:
        return jsonify({"error": "쿼리가 제공되지 않았습니다."}), 400
    print(query)

    try:
        cursor.execute(query)
        if query.strip().upper().startswith('SELECT'):
            results = str(cursor.fetchall())
            print(results)
            return results
        else:
            con.commit()
            return jsonify({"message": "쿼리 실행 완료"}), 200  # OK
    # 실행 오류 시 문구 출력
    except pymysql.MySQLError as err:
        return jsonify({"error": f"SQL 실행 중 오류가 발생했습니다: {err}"}), 500  # Internal Server Error
    finally:
        cursor.close()


# OpenAI assistant API 호출
def chatbot(user_message):
    if client is None:
        return jsonify({"error": "OpenAI 클라이언트가 초기화되지 않았습니다."}), 500  # Internal Server Error

    try:
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_message,
        )
    except Exception as e:
        return jsonify({"error": "메시지 생성 중 오류가 발생했습니다."}), 500  # Internal Server Error

    try:
        # run 객체 생성
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant.id,
        )
    except Exception as e:
        return jsonify({"error": "스레드 실행 중 오류가 발생했습니다."}), 500  # Internal Server Error

    if run.status == 'completed':
        messages = client.beta.threads.messages.list(
            thread_id=thread.id
        )
        print(run.status)
    else:
        print(run.status)

    # AI가 쓸 함수 도구 리스트 정의
    tool_outputs = []

    # required action 상태일 시 적절한 함수 도구 찾기
    if run.required_action and hasattr(run.required_action, 'submit_tool_outputs'):
        for tool in run.required_action.submit_tool_outputs.tool_calls:
            kwargs = json.loads(tool.function.arguments)
            func_name = globals()[tool.function.name](**kwargs)
            if tool.function.name == "get_current_weather":
                tool_outputs.append({
                    "tool_call_id": tool.id,
                    "output": str(func_name)
                })
            elif tool.function.name == "ask_schedule":
                tool_outputs.append({
                    "tool_call_id": tool.id,
                    "output": str(func_name)
                })

    # 모든 함수 도구를 목록으로 수집한 후 한 번에 제출
    if tool_outputs:
        try:
            run = client.beta.threads.runs.submit_tool_outputs_and_poll(
                thread_id=thread.id,
                run_id=run.id,
                tool_outputs=tool_outputs
            )
            print("Tool outputs submitted successfully.")
            print(run.status)
        except Exception as e:
            print("Failed to submit tool outputs:", e)
    else:
        print("No tool outputs to submit.")

    if run.status == 'completed':
        try:
            messages = client.beta.threads.messages.list(
                thread_id=thread.id
            )
            response = [m.content[0].text for m in messages if m.run_id == run.id][0].value
            return jsonify({"response": response})
        except Exception as e:
            return jsonify({"error": "응답 처리 중 오류가 발생했습니다."}), 500  # Internal Server Error
    else:
        return jsonify({"status": run.status})


# Flask 포팅, flask_cors를 통한 다른 서버 요청 활성화
app = Flask(__name__)
CORS(app)


# 엔드포인트 정의, POST 요청
@app.route('/chatbot', methods=['POST'])
def chat():
    try:
        user_message = request.json['message']  # 클라이언트로부터 전송된 JSON 데이터에서 'message' 키의 값을 추출
    except KeyError:
        return jsonify({"error": "메시지가 제공되지 않았습니다."}), 400  # Bad Request

    response = chatbot(user_message)  # 추출된 사용자의 입력 메시지를 'chatbot' 함수에 전달하여 챗봇의 응답 생성
    return response  # 챗봇의 응답을 JSON 형식으로 변환하여 클라이언트에 반환


if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5001, debug=True)
    except Exception as e:
        print("서버 실행 중 오류가 발생했습니다.")