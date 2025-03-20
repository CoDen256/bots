# HomeWorkBot
Telegram bot, that simplifies browsing, editing, adding and deleting current homework for certain date,group etc. Materials, lectures and files for certain subject and homework can be provided either.

## Chain of Commands:
+ <b> /start </b> - User provided with all information needed to use bot.
+ <b> /select </b> [subject] - Selecting one of available subjects
	+ (specify group) - choosing appropriate group (if needed)
	+ <b> /add </b> - Adding a new homework for certain group and subject by specifing all attributes
		* specify topic 
		* specify content
		* specify deadline
		* attach file or photo (optional)
		* provide additional information (optional)
	+ <b> /delete </b> - Deleting an existing homework
	+ <b> /show </b> - user will be provided with all information for current homework
	+ <b> /materials </b> - Uploading all files for this subject (lectures/practical etc)
	+ <b> /select </b> - Selecting a new subject
	
	
### HomeWork object consists following fields:
* <b> subject </b> 	- Subject of chosen homework
* <b> topic </b> 	- Current topic
* <b> content </b> 	- Exactly what is needed to be done
* <b> date </b>		- Deadline
* <b> group </b>	- Group (if exists)
* <b> file </b>		- Attachments (file/photo)
* <b> additional</b>- Additional information
