캠퍼스 조회
---------------------------------------------------------------------------------

.. http:get:: /campus/search

   캠퍼스를 조회하는 API입니다.

   **Example request**:

   .. sourcecode:: http

      GET /campus/search HTTP/1.1
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
            "id": 5629499534213120,
            "univ_name": "건국대학교",
            "campus_name": "서울",
            "service_url": "https://ku.opencampus.kr"
          }
        ]
      ]

   :query q: 검색어
       :statuscode 200: no error
