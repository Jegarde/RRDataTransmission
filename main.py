import recnetpy
import os
import asyncio
import aiohttp
from recnetlogin import RecNetLoginAsync
from dotenv import load_dotenv

# SET THIS TO THE ROOM'S NAME YOU'RE TRANSMITTING DATA TO
ROOM_NAME = ""

# don't touch
last_role = 0 

async def main():
    # Load account credentials
    load_dotenv(override=True)
    
    # Initialize RecNet API wrapper
    recnet = recnetpy.Client()
    
    # Initialize RNL to authorize required API calls
    rnl = RecNetLoginAsync(username=os.getenv("USERNAME"), password=os.getenv("PASSWORD"))
    
    # Validate room (must be public for now)
    resp = await recnet.rec_net.custom("https://rooms.rec.net/").rooms.make_request("get", params={"name": ROOM_NAME, "include": 4}, headers=await get_headers(rnl))
    if resp.status != 200: 
        print("Room not found!")
        await recnet.close()
        await rnl.close()
        return
    
    room = resp.data
    
    # Ask for the player to transmit data to
    while True:
        username = input("Set Rec Room player: ")
        account = await recnet.accounts.get(username)
        
        # Validate account
        if not account:
            print("Account not found!")
            continue
        
        # Make sure not the authorized account
        if account.username == rnl.username:
            print("Can't be the same account as auth!")
            continue

        # Get user's matchmaking info
        match = await recnet.rec_net.custom("https://match.rec.net/").player.make_request("get", params={"id": account.id}, headers=await get_headers(rnl))
        if not match.success:
            print("Failed to fetch matchmaking data!")
            continue
        
        instance = match.data[0].get("roomInstance", {"roomId": -1})
        
        # Check if the user is in the specified room
        if instance and instance.get("roomId") == room["RoomId"]:
            print("Found player!")
            break
        else:
            print(f"Player is not in the room! Room ID: {instance.get('roomId')}")
            
    # Get user's role
    roles = room["Roles"]
    global last_role
    for i in roles:
        if i["AccountId"] == account.id:
            last_role = i["Role"]
            break
     
    # Unused for now   
    #is_co_owner = True if i.id == 30 else False
            
    # Initialize aiohttp client
    conn = aiohttp.TCPConnector(limit=50)
    session = aiohttp.ClientSession(connector=conn)
        
    word = ""
    async with session as _session:
        while True:
            # Reset validation flag
            flag = False
            
            # Menu
            option = input(
                "1. Transmit payload\n"
                "2. Transmit byte\n" \
                "3. Exit\n" \
                "> " \
            )
            
            # Check which option the user chose
            match option:
                case "1":
                    # Prompt for word to transmit
                    word = input("Text (ASCII): ")

                    if word:
                        # Validate byte
                        if len(word) > 512:
                            print("A word can only be 512 characters long!")
                            continue
                        
                        # Turn into binary (ASCII)
                        binary = ascii_to_binary(word)
                        
                    # Signal that I'm starting to transmit text
                    print("\nLetting client know that I'm transmitting a payload...")
                    assert await transmit_byte("00000000", room["RoomId"], account.id, await get_headers(rnl), _session), "Failed"
                        
                    # Transmit content length
                    content_length_byte = "{0:08b}".format(len(word))
                    print(f"\nTransmitting content length... ({len(word)}, {content_length_byte})")
                    assert await transmit_byte(content_length_byte, room["RoomId"], account.id, await get_headers(rnl), _session), "Failed"
                        
                    # Transmit text
                    print("\nTransmitting payload...")
                    assert await transmit_byte(binary, room["RoomId"], account.id, await get_headers(rnl), _session), "Failed"
                    
                    print("Transmitted:", word)
            
                case "2":
                    # Prompt for byte to transmit
                    byte = input("Byte: ")

                    # Validate
                    if byte:
                        if len(byte) != 8:
                            print("A byte must have 8 bits!")
                            continue
                        
                        for i in list(byte):
                            if i not in ("0", "1"):
                                print("Invalid bit!")
                                flag = True
                                break
                            
                        if flag: continue
                            
                        binary = byte
                        
                    # Transmit byte
                    assert await transmit_byte(byte, room["RoomId"], account.id, await get_headers(rnl), _session), "Failed"
                    
                    print("Transmitted:", byte)
                
                case "3": break # Exit
                
                case _: continue
            
        # Give default role back if co-owner
        #if default_role == 30:
        #    await recnet.rec_net.rooms.rooms(ROOM_ID).roles(account.id).make_request("put", body={"role": default_role}, headers=await get_headers(rnl))
        
    await rnl.close()
    await recnet.close()
    
def ascii_to_binary(ascii):
    # Takes a string with ASCII characters and turns it into stringified binary to be transmitted
    return ''.join(format(ord(i), '08b') for i in ascii)


async def transmit_byte(byte: str, room_id: int, account_id: int, headers: dict, session):
    # Transmit a byte to the specified user in a room that supports receiving bytes
    
    global last_role
    index = 0
    
    # Transmit each bit
    for i in byte:
        index += 1
        
        bit = True if i == "1" else False
        if bit == True:
            # Bit == 1
            if last_role == 20:
                last_role = 0
            else:
                last_role = 20
        else:
            # Bit == 0
            if last_role == 10:
                last_role = 0
            else:
                last_role = 10
        
        # Set user's role to the corresponding signal
        async with session.put(f"https://rooms.rec.net/rooms/{room_id}/roles/{account_id}", data=f"role={last_role}", headers=headers) as resp:
            data = await resp.json()
            
            if data and data.get("Success"):
                # Byte progress
                if index % 8 == 0:
                    print(f"Transmitted {index // 8}/{len(byte) // 8} bytes...")
            else:
                print("Failure.")
                if data: print(data.get("Error", "Unknown error."))
                return False
        
    return True


async def get_headers(rnl):
    return {"Authorization": await rnl.get_token(include_bearer=True), "Content-Type": "application/x-www-form-urlencoded"}
    

if __name__ == "__main__":
    asyncio.run(main())
