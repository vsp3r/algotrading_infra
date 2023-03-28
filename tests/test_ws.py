# import asyncio
# import websockets
# import json
# from datetime import datetime

# ### BINANCE VERSION
# # async def connect_to_stream():
# #     uri = "wss://fstream.binance.com/ws"  # Replace with the WebSocket stream URL
    
    
# #     async with websockets.connect(uri) as websocket:
# #         n = 0
# #         symbol = 'ethusdt'
# #         level = 20
# #         speed = 0
# #         stream = "{}@depth{}@{}ms".format(symbol.lower(), level, speed)
# #         s2 = "ethusdt@depth@0ms"
# #         stream = [stream]
# #         # json_msg = json.dumps({"method": "SUBSCRIBE", "params": stream, "id": id})

# #         subscription_message = {
# #             "method": "SUBSCRIBE",
# #             "params": stream # Replace with the actual stream name
# #             # Add any additional fields specific to your subscription message
# #         }
        
# #         await websocket.send(json.dumps(subscription_message))
        
# #         # Create a task to send the unsubscription message after 5 seconds
# #         unsubscription_task = asyncio.ensure_future(send_unsubscription(websocket))
        
     
# #         while True:
# #             message = await websocket.recv()
# #             n += 1
# #             print(f'Recieved message ({n}): {message}')
# #             # Process the received message as per your requirements
# #             if unsubscription_task.done():
# #                 break   
# # # Run the connection functionee
# #                 # Wait for the unsubscription task to complete before closing the connection
# #         await unsubscription_task
        
# #         # Optionally, you can perform any cle
# #         # anup or additional tasks here
# #         await websocket.close()



# # async def send_unsubscription(websocket):
# #     await asyncio.sleep(5)  # Delay before sending the unsubscription message

# #     symbol = 'ethusdt'
# #     level = 20
# #     speed = 0
# #     stream = "{}@depth{}@{}ms".format(symbol.lower(), level, speed)

# #     s2 = "ethusdt@depth@0ms"
# #     stream = [stream]
# #     unsubscription_message = {
# #         "method": "UNSUBSCRIBE",
# #         "stream_name": stream  # Replace with the actual stream name
# #         # Add any additional fields specific to your unsubscription message
# #     }

# #         # json_msg2 = json.dumps({"method": "UNSUBSCRIBE", "params": stream2, "id": id})

# #     await websocket.send(json.dumps(unsubscription_message))


# # asyncio.get_event_loop().run_until_complete(connect_to_stream())
        
# ### HYPERLIQUID VERSION
# import asyncio
# import json
# from datetime import datetime
# import websockets

# async def subscribe_to_stream(websocket):
#     stream = {"type": "l2Book", "coin": "ETH"}
#     subscription_message = {"method": "subscribe", "subscription": stream}
#     await websocket.send(json.dumps(subscription_message))

# async def process_messages(websocket):
#     msg_count = 0

#     try:
#         while True:
#             message = await websocket.recv()
#             msg_count += 1
#             # print(f'Received message ({msg_count}) at {datetime.now()}: {message}')

#             try:
#                 data = json.loads(message)
#             except json.JSONDecodeError:
#                 print(f'Recieved STRING message ({msg_count}): {message}')
#             else:
#                 if "channel" in data and data["channel"] == "subscriptionResponse":
#                     print(f'Recived subscriptionResponse ({msg_count}): {data}')
#                 elif "channel" in data and data["channel"] == "l2Book":
#                     b_count = 0
#                     a_count = 0
#                     for _ in data['data']['levels'][0]:
#                         b_count += 1
#                     for _ in data['data']['levels'][1]:
#                         a_count += 1
#                     print(f'Recived l2Book ({msg_count}) (B:{b_count}, A:{a_count}): {data}')
#                 else:
#                     print(f'Recived OTHER DATA ({msg_count}): {data}')

#     except websockets.exceptions.ConnectionClosedError:
#         print("WebSocket connection closed.")

# async def connect_to_stream():
#     uri = "wss://api.hyperliquid.xyz/ws"  # Replace with the WebSocket stream URL

#     async with websockets.connect(uri) as websocket:
#         # Task for sending subscription message
#         subscribe_task = asyncio.create_task(subscribe_to_stream(websocket))

#         # Task for receiving and processing messages
#         process_task = asyncio.create_task(process_messages(websocket))

#         # Wait for both tasks to complete (or raise an exception)
#         await asyncio.gather(subscribe_task, asyncio.sleep(8))

# # Run the event loop
# asyncio.get_event_loop().run_until_complete(connect_to_stream())


# # async def send_unsubscription(websocket):
# #     await asyncio.sleep(5)  # Delay before sending the unsubscription message

# #     stream = {
# #             "type": "l2Book",
# #             "coin": "ETH"
# #     }

# #     unsubscription_message = {
# #         "method": "unsubscribe",
# #         "subscription": stream  
# #     }

# #     await websocket.send(json.dumps(unsubscription_message))


# # asyncio.get_event_loop().run_until_complete(connect_to_stream())
        
        