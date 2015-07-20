Open Campus
====================

[![Build Status](https://travis-ci.org/shlee322/opencampus.svg)](https://travis-ci.org/shlee322/opencampus)

오픈캠퍼스는 전국 대학교 통합 커뮤니티/포탈 서비스를 목표로 
시작된 프로젝트입니다.

현재 강의 정보 시스템과 기본적인 커뮤니티 기능 또 학교별 확장을 위한
시스템을 지원하고 있습니다.

또한 궁극적으로 각 학교와의 제휴를 통한 유기적인 포탈 연동을 위해 노력하고 있습니다.


## Service

공식 서비스 URL : http://opencampus.kr

정기적으로 매달 1일, 16일에 서비스에 최신 코드가 배포됩니다.

단, 보안 이슈나 오픈캠퍼스 내부 정책에 의해 필요한 경우
검토 후 바로 배포될 수 있습니다.


## License

오픈캠퍼스는 `AGPL v3.0` 라이센스를 적용하고 있습니다.

자세한 사항은 `LICENSE` 파일을 확인해주세요.


## Contribute

오픈캠퍼스는 AGPL 라이센스의 프로젝트로 누구든지 참여하실 수 있습니다.

자세한 사항은 [여기](https://developers.opencampus.kr/contribute.html) 를
참고해주세요.


## Source

```
git clone git://git@github.com:shlee322/opencampus.git
```



## Install

### Installing Dependencies

OpenCampus 프로젝트를 실행하기 위하여 다음과 같은 프로그램이 깔려 있어야 합니다.

+ python3
+ mongodb
+ redis
+ elasticsearch

먼저 opencampus 프로젝트의 최상위 폴더에 다음과 같이 입력하여 Python 의존성 라이브러리를 설치하여 줍니다.

```
pip3 install -r requirements/requirements.txt
```

추가로 문서 자동화 도구인 sphinx를 설치하고자 할 경우 다음과 같이 입력합니다.

```
pip3 install -r requirements/sphinx.txt
```

다음, static 폴더로 들어가 HTML, CSS, JavaScript 의존성 라이브러리를 설치하여 줍니다.

```
bower install
```

### DNS Setting

아래의 내용을 `/etc/hosts` 파일에 추가합니다. (윈도우의 경우 `%WINDIR%\system32\drivers\etc\hosts` 파일)

```
127.0.0.1   opencampus.dev
127.0.0.1   apis.opencampus.dev
127.0.0.1   developers.opencampus.dev
127.0.0.1   test.opencampus.dev
```

### Create Campus

`http://developers.opencampus.dev:5000/console`에 접속하여 캠퍼스를 추가합니다.

캠퍼스 추가 후 해당 캠퍼스를 클릭하여 Domain에 `test.opencampus.dev:5000`를 입력후 저장 버튼을 클릭합니다.

캠퍼스를 추가하면 `http://test.opencampus.dev:5000`를 통하여 테스트 캠퍼스를 볼 수 있습니다.
