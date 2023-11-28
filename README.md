# Networks Assignment 2

## Group Project by Brad Didier, Kaleb Bishop, and Matthew Bryant

## Description:
This project consists of both a server and client file. When connected to the server, clients are able to join group message rooms and send messages between clients connected to the same server and group. To run this project, launch the server.py program and at least one client.py program instance. User interaction occurs in the client program, where the user can enter the following commands:

## Available Terminal Commands
### Part 1 Commands
"%join" --> joins the default group message board
"%post subject content" --> posts a message to the default board
"%users" --> retrieves a list of all users in default group
"%message messageID" --> retrieves contents of specified message
"%leave" --> leaves the current group
"%exit" --> disconnect from the server and shutdown the client
### Part 2 Commands
"%groups" --> retrieve a list of all groups that can be joined
"%groupjoin groupID" --> join the specified group
"%grouppost groupID subject content" --> posts a message to the specified group
"%groupusers groupID" --> retrieves a list of users in the specified group
"%groupleave groupID" --> leave a specific group.
"%groupmessage groupID messageID" --> retrieves the content of the message posted earlier on a message board in the specified group

## Major Issues Encountered
One major issue our group encountered during this project was when we were figuring out how to implement the client's ability to receive messages from the server. At first we created a receive message function but quickly realized we wouldn't always be able to call this function when the server sent a message. We eventually overcame this obstacle by implementing the ReaderThread function seen in client.py. Another issue we had throughout the course of development was on how to handle server side issues. If we did not choose to send them to the client we would risk reading from the server while expecting one thing but instead receiving an error message from an earlier server side operation. We eventually overcame this problem by standardizing what was sent between server and client.