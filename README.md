OpenAI API를 활용한 AI 일정관리 챗봇 서비스.
OpenAI에서 제공하는 Assistants API를 기반으로 제작.
Assistants Function Calling 기능을 사용하여 기상정보를 제공, 일정 데이터를 등록 • 수정 • 조회하는 SQL문 작성.
- get_current_weather -
  OpenWeatherMap의 기상예보 API를 통해 받은 기상정보를 제공하는 함수
- ask_schedule -
  사용자의 요구사항을 적절한 SQL문으로 작성 후 커밋
