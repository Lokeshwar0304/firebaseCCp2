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