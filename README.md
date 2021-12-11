# 실리콘밸리에서 날아온 데이터 엔지니어링 스터디 6기

## Git 사용 방법

> 본 영역에서는 강사의 repository를 base code로 두고 이를 자신의 서버에 올리는 방법을 설명합니다.

### A. 기존에 작업한 내용물 제거하기

⚠️ 잠깐!
이 작업을 진행하면 기존의 airflow/dags 디렉토리의 내용물이 날아갈 수 있습니다.
작업을 진행하기에 앞서, 안전한 곳(컴퓨터 바탕화면 등)에 현재 작성한 코드를 저장해주세요.


#### 1단계. 서버 접속하기
1. ssh로 본인의 ec2 서버에 접속
2. airflow 디렉토리로 이동

### 2단계. 기존에 작업하던 내용물 제거하기

1. dags 폴더 제거하기
  * `rm -rf dags`
2. 기존에 연결된 git 설정이 있다면 이를 제거하기
  * 기존에 연결된 git 설정이 있는지는 `ls .git` 명령어를 통해 알 수 있음
    * `ls .git` 했을 때 `ls: cannot access '.git': No such file or directory`메시지가 나온다면 → 기존에 연결된 git이 없다는 뜻이므로 스킵
    * `ls .git` 했을 때 `branches  description  HEAD {이하 생략}` 같은 메시지가 나온다면 → 기존에 연결된 git이 있다는 뜻이므로 `rm -r .git` 명령어로 연결 해제

### B. 원본 repository Fork 뜨기

1. base가 될 Max의 repository를 복사해, 내 Repository로 만들기
  * 강사의 Github repository로 이동하여, 화면 우상단의 `[Fork]` 버튼 클릭
  * \[참고] 6기의 경우 강사의 Github repository는 다음과 같음: https://github.com/keeyong/data-engineering-batch6
2. git 주소 복사하기
  * 화면 우상단의 초록색 `[Code]` 버튼 클릭
  * `https://github.com/...` 오른쪽의 복사 버튼(네모 두개 겹친 모양) 클릭


### C. 내 서버에서 Fork한 repository 사용하기


1. airflow를 git respository로 만들기
  * `git init`
2. 로컬 repository와 앞서 Fork뜬 repository 연결해주기
  * `git remote add -f origin {2단계-B에서 복사한 주소}`
    * \[참고] 보통 다음과 같은 형식일것임: `git remote add -f origin https://github.com/{자신의Github유저이름}/data-{어쩌고저쩌고}.git`
  * `git config core.sparseCheckout true`
  * `echo "dags" >> .git/info/sparse-checkout`
  * `git pull origin main`
  * `git branch --set-upstream-to=origin/main master`
  * `git pull`
3. 연결이 잘 됐는지 확인하기
  * `ls dags` 명령어 입력했을 때 에러가 안뜨면 성공




