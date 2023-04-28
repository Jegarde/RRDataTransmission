# Control panel for transmitting data to Rec Room

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
