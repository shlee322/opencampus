오픈캠퍼스 개발 참여 방법
=================================================================================

오픈캠퍼스는 AGPL을 따르는 오픈소스 프로젝트입니다.

Slack
---------------------------------------------------------------------------------

오픈캠퍼스에서는 실시간 소통을 위하여 Slack를 운영하고 있습니다.

아래에 이메일을 적어주신다음 초대요청을 눌러주세요.

.. raw:: html

    <div style="margin:10px;">
        <form action="/_/invite_slack" method="GET">
            <input type="email" class="form-control" name="email" placeholder="support@opencampus.kr">
            <button type="submit" class="btn btn-default">초대 요청</button>
        </form>
    </div>



Github
---------------------------------------------------------------------------------

Source:
    git clone git@github.com:shlee322/opencampus.git


0-Day 취약점 보고
---------------------------------------------------------------------------------

   **0-Day 취약점** 의 경우 이슈트래커가 아닌 support@opencampus.kr 로 패치 파일을
   보내주십시오.


개발 가이드
---------------------------------------------------------------------------------

**Python Code**:

1. PEP8을 준수하여야 합니다.
2. 파이썬 코드 파일 가장 앞 부분에는 아래의 주석과 한줄의 빈 줄 삽입되어야 합니다.

::

  # -*- coding: utf-8 -*-
  # Copyright (C) 2015 opencampus.kr
  #
  # This program is free software: you can redistribute it and/or modify
  # it under the terms of the GNU Affero General Public License as published by
  # the Free Software Foundation, either version 3 of the License, or
  # (at your option) any later version.
  #
  # This program is distributed in the hope that it will be useful,
  # but WITHOUT ANY WARRANTY; without even the implied warranty of
  # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  # GNU Affero General Public License for more details.
  #
  # You should have received a copy of the GNU Affero General Public License
  # along with this program.  If not, see <http://www.gnu.org/licenses/>.

3. 문자열의 경우 어쩔 수 없는 경우를 제외하고는 유니코드를 사용하여야 합니다.

::

  u'test' # O
  'test'  # X

**Branch Name**:

  - bug/이슈ID
  - feature/이슈ID

**Commit Message**:

1. Fixed Bug
::

  Fixed Bug: 로컬 개발 환경에서 URL 버그 수정

  로컬 개발 환경에서 캠퍼스 사이트들의 하단 링크 클릭시
  접속이 안되는 문제를 해결함

  Implements: #3 위키 기능 구현
  Fixes: #1, #2


2. New feature

::

  New Feature: 위키 기능 구현
  
  아래와 같은 기능을 구현함
  
  * 위키 검색
  * 위키 보기, 수정
  * 위키 히스토리
  
  Closes : #3 
