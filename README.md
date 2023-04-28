# Control panel for transmitting data to Rec Room

### Good to know
- This is an early version of the project and is subject to change dramatically.
- Contact Jegarde#3484 on Discord if you're struggling to make it work.
- The limit for payloads is 65 characters. This will change in the future.
- The room is made using beta chips and is vulnerable to breaking.
- Room moderators & hosts should have no permissions due to the method used.
- Feel free to modify all of the source code to your own interests.

### How does this work?
There's CV2 chips for checking if a player is a host, mod or a co-owner and you can modify a player's roles through the API. This allows me to send remote signals to the specified player while CV2 is constantly checking for each players' roles locally.

So let's assume the specified player doesn't have roles by default. The signals would be the following
```
Host = Add on bit
Mod = Add off bit
None = Repeat previous bit
```

Then with Python, I enter my byte and it sends each bit by modifying the player's role through the API according to the signals. So if I wanted to send `1011` in binary, the following calls would be made:
```py
>>> Modify [player] role to Host # Add on bit
>>> Modify [player] role to Mod  # Add off bit
>>> Modify [player] role to Host # Add on bit
>>> Modify [player] role to None # Add on bit (repeat previous bit)
```

And once 8 bits have been sent, CV2 will save the byte and clear the buffer.

### Setup
1. Clone [^DataTransmissionTemplate](https://rec.net/room/DataTransmissionTemplate)
2. Download the source code of the control panel here.
3. Enter your account's credentials into `.env` to give the control panel access to the room.

      a. You can alternatively make an alt account a co-owner and use that account instead.
      
      b. You will not be able to transmit data to the alt account.
      
4. Enter the room's name into the `ROOM_NAME` variable found at the top of `main.py`

### Usage
1. Run `main.py`.
2. Enter the account's username you want to transmit data to.

      a. The account must be in the room.
      
      b. The account cannot be the same one set to `.env` or the owner of the room.
   
3. You can now transmit a payload (strings) or a single byte.


