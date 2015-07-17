강의 검색
---------------------------------------------------------------------------------

.. http:get:: /campus/(int:campus_id)/lectures/search

   캠퍼스의 강의를 검색하는 메소드입니다.

   쿼리를 사용할 수 있으며 쿼리는 다음과 같습니다.

   **Example request**:

   .. sourcecode:: http

      GET /campus/5629499534213120/lectures/search HTTP/1.1
      Host: apis.opencampus.kr
      Accept: application/json, text/javascript

   **Example response**:

   .. sourcecode:: http

      HTTP/1.1 200 OK
      Vary: Accept
      Content-Type: text/javascript

      {
        "data": [
          {
            "id": 10231412434124,
            "name": "컴퓨터공학부"
          }
        ]
      ]

   :statuscode 200:
       :statuscode 404: 캠퍼스가 존재하지 않음




