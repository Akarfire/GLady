
// Which meme box is currently displayed (0 or 1)
let currentMemeBox = 0;

// Audio context
const audioContext = new AudioContext();

let isAudioUnlocked = true;

//
let isImageInSpeakMode = false;

// Busy flag
let isTtsPlaying = false;

// Queed memes, awaiting there time to be played
let ttsQueue = Array();

// Adress of an HTTP server that contains image and audio files.
let resourceServerAddress = "";

let speakingImageName = "";
let silentImageName = "";

let mute = false;
let mute_local = false;

// Audio nodes
let audioCtx;
let sourceNode;
let gainNode;

let socket;


// Data structure for storing queued memes
class queuedTTS
{
    constructor(text, initiatorName, nameColor, audioVolume, audioFile)
    {
        this.text = text;
        this.initiatorName = initiatorName;
        this.nameColor = nameColor;
        this.audioVolume = audioVolume;
        this.audioFile = audioFile;
    }
}


// Wait for the HTML file to be fully loaded before running the code
document.addEventListener("DOMContentLoaded", onFileLoaded);

function onFileLoaded()
{
    initAudioNodes();

    // Unlocking audio context
    document.addEventListener("click", async () => {
        if (audioContext.state === "suspended") 
        {
            await audioContext.resume();
            console.log("Audio unlocked!");
            isAudioUnlocked = true;
        }
    });

    // Control buttons
    const popOutButton = document.getElementById("popout_button");
    if (popOutButton)
        popOutButton.addEventListener("click", openPopoutVersion);

    const muteButton = document.getElementById("mute_button");
    if(muteButton)
        muteButton.addEventListener("click", 
        function () 
        {
            if (socket && socket.readyState === WebSocket.OPEN)
                socket.send(JSON.stringify({Command: "ToggleMute"}));
        }
    );

    const muteLocalButton = document.getElementById("mute_local_button");
    if(muteLocalButton)
        muteLocalButton.addEventListener("click", 
            function () 
            {
                mute_local = !mute_local; 

                const audioElem = document.getElementById("audio");

                if (mute_local)
                    muteLocalButton.textContent = "Unmute Local";
                else
                    muteLocalButton.textContent = "Mute Local";

                if (mute || mute_local)
                    audioElem.volume = 0.0;
                else
                    audioElem.volume = 1.0;
            }
        );

    // Connecting to the server
    connect();

    // Initiaing update loop
    setInterval(update, 500);
}

function initAudioNodes()
{
    if (audioCtx) return;

    const audioElem = document.getElementById("audio");

    // Create an AudioContext for the first meme box
    audioCtx = new AudioContext();

    sourceNode = audioCtx.createMediaElementSource(audioElem);
    gainNode = audioCtx.createGain();
    gainNode.gain.value = 1.0; 

    // source -> pitch -> gain -> destination
    sourceNode.connect(gainNode);
    gainNode.connect(audioCtx.destination);
}

function connect()
{
    socket = new WebSocket("ws://localhost:8003");

    socket.onopen = () => {
        console.log("Connected to server!");
    };
    
    socket.onmessage = (event) => {
        try 
        {
            // WebSocket messages are text (UTF-8 decoded by default)
            const data = JSON.parse(event.data);

            console.log("Receiving message data: ", data);

            // Processing command messages
            if (typeof data.TTS_Command === "string")
            {
                // Resource server address
                if (data.TTS_Command == "SetResourceServerAddress")
                {
                    if (typeof data.ResourceServerAddress === "string")
                        resourceServerAddress = data.ResourceServerAddress
                } 

                // Image names
                if (data.TTS_Command == "SetImageNames")
                {
                    if (typeof data.SpeakingImageName === "string" && typeof data.SilentImageName === "string" )
                    {
                        speakingImageName = data.SpeakingImageName;
                        silentImageName = data.SilentImageName;

                        setSilent();
                    }
                } 

                // Mute command
                if (data.TTS_Command == "ToggleMute")
                {
                    mute = !mute; 

                    const audioElem = document.getElementById("audio");
                    const muteButton = document.getElementById("mute_button");

                    if (mute)
                        muteButton.textContent = "Unmute";
                    else
                        muteButton.textContent = "Mute";

                    if (mute || mute_local)
                        audioElem.volume = 0.0;
                    else
                        audioElem.volume = 1.0;
                }
            }

            // Validate required fields
            else if (typeof data.TTS_File === "string" && typeof data.Text === "string" && typeof data.UserName === "string") 
            {
                const randomColor = nameToColor(data.UserName);

                let audioVolume = 1.0;
                if (typeof data.Volume === "number")
                    audioVolume = data.Volume;

                // Putting a new meme in to the queue
                let qTTS = new queuedTTS(data.Text, data.UserName, randomColor, audioVolume, resourceServerAddress + "/Resources/TTS/" + data.TTS_File);
                ttsQueue.push(qTTS);
            } 

            else 
            {
                console.warn("Received malformed message data:", data);
            }
        } 

        catch (err) 
        {
            console.error("Failed to parse WebSocket message:", err, event.data);
        }
    };

    socket.onerror = (err) => {
        console.error("WebSocket error:", err);
    };

    socket.onclose = () => {
        console.log("Disconnected from server");
        setTimeout(connect, 5000);
    };
}

// Processes the queue of memes
function update()
{
    if (ttsQueue.length > 0 && !isTtsPlaying)
    {
        let tts = ttsQueue.shift();

        playTTS(tts.text, tts.initiatorName, tts.nameColor, tts.audioVolume, tts.audioFile);
    }

    else if (isImageInSpeakMode && !isTtsPlaying)
    {
        isImageInSpeakMode = false;

        setSilent();
    }
}

function setSilent()
{
    const container = document.getElementById("container");
    container.querySelector(".image").src = resourceServerAddress + "/Resources/TTS/" + silentImageName;
    container.querySelector(".subtitle").style.opacity = "0";
}

// PLAYS THE MEME!
async function playTTS(text, initiatorName, nameColor, audioVolume, audioFile)
{
    // Update busy flag
    isTtsPlaying = true;
    isImageInSpeakMode = true;

    const audioObj = new Audio();
    audioObj.src = audioFile;

    // Try to load audio
    const audioDecoded = await new Promise((resolve) => {

        // Successfully loaded
        audioObj.addEventListener("canplaythrough", () => resolve(true), { once: true });

        // Failed to load
        audioObj.addEventListener("error", () => resolve(false), { once: true });
    });

    if (audioDecoded)
    {
        const audioElem = document.getElementById("audio");
        audioElem.crossOrigin = "anonymous";
        audioElem.src = audioObj.src;
        console.log(audioVolume);

        gainNode.gain.value = audioVolume; 

        let duration = audioObj.duration;
        audioElem.onerror = () => { duration = 2; }


        const container = document.getElementById("container");
        container.querySelector(".image").src = resourceServerAddress + "/Resources/TTS/" + speakingImageName;
        container.querySelector(".user_name").style.color = nameColor;
        container.querySelector(".user_name").textContent = initiatorName + ":";
        container.querySelector(".text").textContent = text;
        container.querySelector(".subtitle").style.opacity = "1";


        setTimeout( () => { isTtsPlaying = false; }, duration * 1000);

        audioElem.play();
    }
}


// This was generated by ChatGPT
function nameToColor(name) 
{
    // Simple hash function to turn the string into a number
    let hash = 0;
    for (let i = 0; i < name.length; i++) 
    {
        hash = name.charCodeAt(i) + ((hash << 5) - hash);
    }

    // Map hash to a hue (0–360)
    const hue = Math.abs(hash) % 360;

    // Use HSL for vivid, consistent colors
    return `hsl(${hue}, 70%, 60%)`;
}


function openPopoutVersion() 
{
    const url = document.URL;
    const features = "width=400,height=500,menubar=no,toolbar=no,location=no,status=no,resizable=yes,scrollbars=no";
    const chatWindow = window.open(url, "TextToSpeech", features);
}