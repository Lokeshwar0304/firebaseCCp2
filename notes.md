request queue
    user send
        1. users sends the user_id
        2. location of request
        3. -> req_type##user_id##latitude##longitude
    unknown send
        1. user sends the user face footprint
        2. location of request
        3. -> req_type##image_foot_print##latitude##longitude


cloud functions <--> redis === need to set serverless vpc
set vpc connector for cloud function to get redis connection

https://stackoverflow.com/questions/63679582/multiple-pub-sub-subscribers-in-one-application

{"victim_id": "7HWiG7KSSjRhfzNYkcQ7tJDZisP2", "blood_group": "AB-", "timestamp": 1619685304168, "latitude": 33.4095205, "longitude": -111.9206227}
01InEPZ89inOwt48Bfft
{"victim_id": "01InEPZ89inOwt48Bfft", "blood_group": "AB-", "timestamp": 1619685304168, "latitude": 33.4095205, "longitude": -111.9206227}