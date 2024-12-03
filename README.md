# AI Mate
AIMate는 Flask 기반의 RESTful API로, OpenAI와 MariaDB를 활용한 챗봇 및 기상 정보를 제공하는 시스템입니다. 이 프로그램은 사용자의 일정 관리와 챗봇 대화, 그리고 기상 정보를 제공하는 기능을 제공합니다.
## 기능 소개
1. 챗봇 기능:
- OpenAI API를 이용하여 사용자가 입력한 메시지에 대한 답변을 생성합니다.
- 챗봇을 통해 다양한 질문과 대화가 가능합니다.
2. 기상 정보 제공:
- OpenWeatherMap API를 이용하여 특정 도시의 현재 날씨 정보를 제공합니다.
- 기온, 체감 온도, 습도, 바람 속도 등 다양한 날씨 정보를 반환합니다.
3. 일정 관리:
- MariaDB와 연동하여 사용자의 일정 정보를 저장하고 조회할 수 있습니다.
- 사용자 인증 토큰을 통해 각 사용자의 고유한 일정을 관리합니다.
## 주요 기술
- OpenAI API: OpenAI의 GPT 모델을 이용하여 사용자와의 대화를 처리합니다.
- OpenWeatherMap API: 현재 날씨 정보를 조회하기 위해 사용되었습니다.
- Flask: Python을 사용하여 RESTful API 서버를 구축하였습니다.
- Flask-CORS: 다양한 출처에서 API를 호출할 수 있도록 Cross-Origin Resource Sharing을 설정하였습니다.
- MariaDB: 사용자의 일정 정보를 저장하기 위해 데이터베이스로 MariaDB를 사용하였습니다.
## 설치 및 실행 방법
### 요구 사항
- Python 3.x
- OpenAI API
- OpenWeatherMap API
- Maria DB 서버
### 설치 방법
1. 라이브러리 설치:
아래 명령어를 사용하여 필요한 Python 라이브러리를 설치합니다.
```
pip install flask pymysql requests flask-cors openai
```

2. 환경 변수 설정:
AIMate.py 파일에서 다음과 같은 값을 설정합니다.
- weather_api_key에 OpenWeatherMap API 키를 입력합니다.
- api_key 및 assistant_id에 OpenAI API 키와 관련 정보를 입력합니다.
- MariaDB 연결 정보를 설정합니다 (host, user, password, db 등).

3. 서버 실행:
아래 명령어로 서버를 실행합니다.
```
python AIMate.py
```
