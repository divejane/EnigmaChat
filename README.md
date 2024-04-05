# DiscreetDial

DiDi, but in the terminal! Revolutionary. Doesn't get much better than this. There's really not a whole lot else to be excited for, people!

## TODO (security, efficiency, etc.) 

### Client/Server tramsmisssion protocol switch to HTTP
Currently running the client/server protocol on TCP just because that's what we have the P2P protocol running on. Eventually going to switch client/server to HTTP because we have just about everything there based on a query/recieve structure.

### Message order verification 
This one is simple; We're just going to tack on a (time sent) section on a message packet after it's sent from the sender's client. From there, the recieving client(s) can determine the order of the messages based off of who sent what first.

## Minor changes:
- Server only sends connection information to join-clients if that client explicitly requests the information of that room. Small change, and honestly won't change a whole lot, but at least somewhat avoids sending a massive list full of a connection information to a (potentially malicious) client
