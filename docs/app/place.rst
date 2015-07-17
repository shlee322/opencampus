장소 검색
---------------------------------------------------------------------------------

.. http:get:: /campus/(int:campus_id)/places

   캠퍼스의 주요 건물이나 장소를 검색하는 기능입니다.

   **Example request**:

   .. sourcecode:: http

      GET /campus/(int:campus_id)/search HTTP/1.1
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
            "main_name": "새천년관",
            "sub_name": ["새관", "새천년관", "새천년기념관"]
            "lat": 0.0,
            "lng": 0.0
          }
        ]
      ]

   :query q: 검색어
       :statuscode 200: no error

