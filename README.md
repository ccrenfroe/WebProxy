# Web Proxy

## CODE
### INPUT READER
My code consists of a few parts. I split it into an input reader, that has a cleanURL function as a subcomponent. Together, these parse through the user input to separate out the parts of the first line that I need to run the proxy with the correct variables. They also handle all of the error checking in the Readline. In essence, they just make sure the user is putting in the right things, and then spitting it back out in a cleaner, easier to use way.

## HEADERGATHERER
The headergatherer does similar work with the headers. It parses them and puts them into a list to be spit back out for easy use. It also does error checking on the headers to make sure they are input in the correct way.

## CLIENT THREAD
The client thread does all of the work. It is basically my new main. It reads in the input from the user , first taking in the new line and then the headers. For the firstline, I read it 1 byte at a time, to insure I do not take too much info and end up taking the headers. THis is a bit inefficient, but it gets the job done and it was the only way I could think of since sockets can't readLine. The headerIn line then takes in all 1024 bytes at a time it can, as there shouldn't be an issue with overreading here.

After that, I run the required functions to break down the data that was received and break it down into my required variables. They are then sent over in an organized manner to the server, and then the response is read back and finally spit back out to the user.

## MAIN
The main just checks to make sure the user enters a port number to connect to and that it is valid, i.e. a number and not a string or some other garbage input. Then, it continuously loops and accepts connections until it has hit 100 connections. After that, the program closes.

## DISCUSSIONS
I discussed with my classmates about how to error check and for edge case bugs I was having. I helped answer questions about how the error checking should work, and where it should be output to. I asked questions such as when the program should end, after 100 connections or if it should dynamically keep track of connections, and what to do about the firefox "spam connections" I kept receiving. Overall, we only asked questions regarding how the program should operate and comparing bugs we may have shared.

## ESTIMATED TIME
For the estimate, puting the pieces together alone probably took about 16 hours total. About 8ish Saturday, and 8ish Sunday. Saturday consisted of smoothing out previous bugs and getting the error checking up and running. Sunday consisted of implementing everything together and error checking my whole program. I also ended up getting some logical errors I had to think through that would amount to about 2ish hours of debugging. Overall, not that bad and I found it enjoyable. 
