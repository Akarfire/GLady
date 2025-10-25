
# Core Components


### 1. Communication Bus

Handles Core-Core and Plugin-Core communications, by routing messages to their receiver addresses.


### 2. Config Controller

Reads and parses the Config.txt file, processes Core options and stores Plugin options.

##### Requests:

1. PluginConfigRequest: - sends back the lines from a specified config file section
	Input:
	*  *ConfigSection*  - the section of config file to retrieve;
	Output:
	* *ConfigLines* - the lines from the config section;

2. RequestAllOptions: - sends back the dictionary of all Core options
	Output:
	* *Options* - the dictionary of all Core options;


### 3. Instruction Processor

Handles Instructions by rerouting them to the executors. Also handles parsing instruction code and interpreting it.

##### Instructions:

1. INSTRUCTIONS_InterpretInstructions: - runs parsed instructions 
	Input:
	*  *Instructions*  - the list of parsed instructions to interpret;
	* *RuntimeParameters* - the list of runtime parameters;

2. FLOW_RunSection_IF_EQ: - runs a code section if 'L' is equal to 'R'
	Input:
	*  *L*  - first operand;
	*  *R* - second operand;
	* *Section* - the name of the code section to run

	FOR DEVS:
		When this instruction is called Runtime parameters MUST contain 'Code', which is the portion of instruction code, which has the required code section. Commands handle this automatically. 

3. FLOW_RunSection_IF_NotEQ: - runs a code section if 'L' is NOT equal to 'R'
	Input:
	*  *L*  - first operand;
	*  *R* - second operand;
	* *Section* - the name of the code section to run

	FOR DEVS:
		When this instruction is called Runtime parameters MUST contain 'Code', which is the portion of instruction code, which has the required code section. Commands handle this automatically. 
	
4. DATA_Store: - stores all given arguments into Global Variables, that can be accessed as runtime parameters from any instruction
	Input:
	*  Argument to Store 1;
	*  Argument to Store 2;
	*  ...

##### Requests:

1. INSTRUCTIONS_ParseInstructionCode: - converts instruction code into actual instructions (parsed instructions)
	Input:
	*  *Code*  - the list of lines of code to parse;

	Output:
	* *Instructions* - the list of parsed instructions


### 4. Plugin Manager

Handles plugin loading, initialization and updating. Handles all Plugin-Plugin communications and puts Plugins to the Communication Bus (or vice-versa) in case of Plugin-Core communications.




# Plugins


### 1. YouTube Chat Reader

A plugin that reads YouTube chat.

##### Events:

1. OnChatMessageArrived: - cast when a new chat message has arrived
	Data:
	*  Chat message that arrived;


### 2. Twitch Chat Reader

A plugin that reads Twitch chat.

##### Events:

1. OnChatMessageArrived: - cast when a new chat message has arrived
	Data:
	*  Chat message that arrived;


### 3. Text To Speech

A plugin that converts text to speech and plays it, also capable of playing SFX.

##### Instructions:

1. TTS_ConvertTTS: - converts given text to speech and stores it in a temp file.
	Input:
	* *TEXT* - The text to convert;

2. TTS_PlayTTS: - plays the last converted TTS
	Input:
	* *UID* - the unique id of the Play TTS call that is going to be put into the finished event;

3. TTS_PlaySFX: - plays the specified sound effect file (from the SFX folder).
	Input:
	* *File* - the name of the SFX file (from the SFX Folder);
	* *Volume* - the volume multiplier of the sound effect;
	* *UID* - the unique id of the SFX call that is going to be put into the finished event;

##### Events:

1. TTS_FinishedPlayingTTS: - cast when TTS has stopped playing
	Data:
	*  *UID* - the unique id of the TTS play call;

2. TTS_FinishedPlayingSFX: - cast when SFX has stopped playing
	Data:
	*  *UID* - the unique id of the SFX play call;


### 4. OBS WebSocket

Allows the use of the OBS web socket to control OBS and do fun things. 

##### Instructions:

1. OBS_SetFilterEnabled: - sets the sources filter enabled status.
	Input:
	* *Source* - the target source;
	* *Filter* - the target filter;
	* *NewEnabled* - new enabled status;

2. OBS_SetItemEnabled: - sets the item (in a specified scene) enabled status.
	Input:
	* *Scene* - the target item's scene;
	* *Item* - the target item name;
	* *NewEnabled* - new enabled status;


### 4. Message Processor

Catches the OnChatMessageArrived event, filters the message and calls for COMMAND_ProcessMessageCommands instruction to run the commands in the message.


### 5. Command Processor

Processes chat message commands. Allows for various command declarations and customization. All commands execute strictly in order, no parallel command execution is allowed.

##### Command Attributes:

* *priority* < integer > - the priority of the command when it is processed in the message, the lower the value - the earlier the command will be executed;

* *ControlServerOnly*

##### Instructions:

1. COMMAND_ProcessMessageCommands - scans and executes all of the commands in the given chat message.
	Input:
	* *Message* - the chat message;
	* *WasFiltered* - were the contents of the message found inappropriate;

2. COMMAND_Finish - finishes execution of the current command.

3. COMMAND_ExecuteCommand - executes the requested command
	 Input:
	* *Command* - the name of the requested command;
	* *Message* (Optional) - simulates the Text of the chat message, if the command requires it; 


### 6. Stream Events

Allows the creation of "stream events". Act similar to commands, but allow for parallel execution. Events have duration time. While events are active, they are updated.

##### Instructions:

1. EVENTS_CallEvent - Calls the requested event (puts it into the call queue)
	Input:
	* *EventName* - the general name of the requested event;
	* *Any other input argument will be passed as a parameter to the event*

2. EVENTS_PauseEvent - Pauses the requested event
	Input:
	* *GeneralName* - the general name of the requested event;
	* *UniqueName* (Optional) - the unique name of the requested event;

3. **TO BE IMPLEMENTED** EVENTS_UnPauseEvent - Un pauses the requested event
	Input:
	* *GeneralName* - the general name of the requested event;
	* *UniqueName* (Optional) - the unique name of the requested event;

4. EVENTS_FinishEvent - Forcefully finishes the requested event
	Input:
	* *GeneralName* - the general name of the requested event;
	* *UniqueName* (Optional) - the unique name of the requested event;


### 7. Wheel Spin

Create custom random wheels with various results and run-time customization!

##### Instructions:

1. SPINS_SpinWheel - Starts spinning the requested wheel
	Input:
	* *SpinWheelName* - the name of the specified wheel;

2. SPINS_ResetWheel - Resets the wheel (used in cases of exclude-result wheels)
	Input:
	* *SpinWheelName* - the name of the specified wheel;

3. SPINS_AddResult - Adds new result(s) to the specified wheel
	Input:
	* *SpinWheelName* - the name of the specified wheel;
	* *Result* - a string of new results separated with '|' (will be just one result if there is no separators);

4. SPINS_ClearResults - Completely deletes the whole result list of the wheel, usually used for clearing out the wheel before using SPINS_AddResult
	Input:
	* *SpinWheelName* - the name of the specified wheel;
