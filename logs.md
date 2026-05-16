7:28 PM 5/11/2026
I was toying around with ideas to help me learn cybersecurity concepts, I thought to create an SOC dashboard that monitors system logs, regardless of the type, and uses a classical
ML approach for anomaly detection. When an anomaly is detected, claude is invoked to give threat assesments and classify the alert as *nothing of concern, a MITRE ATT&CK tactic and the threat category and severity level. I realized that a lot of actual attack logs are either proprietary or counterproductive to use, so THEN I had the idea to also have claude generate my logs. 

7:39 PM 5/11/2026
Because this is for the sake of my learning, and because eventually I may have to explain exactly how this works, this is going to be made by hand, save for UI elements.

7:44 PM 5/11/2026
Im going to start with the log parsing code, this will be the heart of the project. I want my program to be able to parse logs from windows, linux and whatever else, so I need to go study some damn logs. 


5:48 PM 5/15/2026
I haven't had a ton of time to work on things, but I had enough downtime at work today that I was able to write my attack log synthesizer, and a real time streamer to play them with. Claude seems to be able to generate pretty accurate ones, even on haiku. I added different params for operating systems (just linux and windows right now), different modes of attack, and duration. This is a pretty solid foundation for some anomaly detection engineering. 
6:00 PM 5/15/2026
Trying to figure out how github work so I can get my first commit on there lol
6:05 PM 5/15/2026
Ok I think figured it out, got the generator and the streamer up, probably going to add these logs too for posterity