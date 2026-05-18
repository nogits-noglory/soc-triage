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
6:43 PM 5/15/2026
Someone dear to me made a very good point: anomalous activity is only anomalous compared against a baseline of unremarkability. So for every malicious log, I should also be generating inconsequential ones. To take it one step further, every log should have an accompanying network group/log. I'm gonna see if I can bang that out before it gets too late. It's been a long ass week
2:23 PM 5/17/2026
I've finished with the network companion for the generator, its looking pretty nice. So now using the linux or windows profiles will generate a complete network companion log; two logs, one incident. Additionally, there are now profiles to generate boring, unremarkable logs with authorized logins and normal lateral movement. A normal workday basically. Committing now. 
2:30 PM 5/17/2026
I realized I hard coded the date I started in the prompts, so all logs are from may 14th lol. Fixing that now. 
2:49 PM 5/17/2026
Now that that's done, the last thing I want to add before I start on my xgboost classifier is a randomized or editable environment profile to accompany each log. So with each log generated, there will also come a complete network profile with a name, devices, authorization schema 
3:07 PM 5/17/2026
Realized that logs of the same os and kind are overwriting eachother in the saved logs file. Quick fix, I added a timestamp system to distinguish them all with
3:14 PM 5/18/2026
Left work early today to job search like my life depends on it... AND finish up the environment template for the generator. Now when you generate logs, you can generate a fictional corporate environment with subnets, devices, a name and all. This can be generated randomly, or you can give a parameter like "law office - 4 employees". This is coming along very nicely. Committing now