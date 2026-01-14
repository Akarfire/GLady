
// Which meme box is currently displayed (0 or 1)
let currentMemeBox = 0;

// Audio context
const audioContext = new AudioContext();

// Whether any meme box is currently visible
let isMemeBoxShown = false;

// Busy flag
let isMemePlaying = false;

// Queed memes, awaiting there time to be played
let memeQueue = Array();

// Data structure for storing queued memes
class queuedMeme
{
    constructor(memeName, initiatorName, nameColor)
    {
        this.memeName = memeName;
        this.initiatorName = initiatorName;
        this.nameColor = nameColor;
    }
}


// Wait for the HTML file to be fully loaded before running the code
document.addEventListener("DOMContentLoaded", onFileLoaded);

function onFileLoaded()
{
    // Unlocking audio context
    document.addEventListener("click", async () => {
        if (audioContext.state === "suspended") 
        {
            await audioContext.resume();
            console.log("Audio unlocked!");
        }
    });

    // Control buttons
    const popOutButton = document.getElementById("popout_button");
    if (popOutButton)
        popOutButton.addEventListener("click", openPopoutVersion);

    const clearButton = document.getElementById("clear_button");
    if(clearButton)
        clearButton.addEventListener("click", clearMeme);

    // Connecting to the server
    connect();

    // Initiaing update loop
    setInterval(update, 500);
}

function connect()
{
    const socket = new WebSocket("ws://localhost:8001");

    socket.onopen = () => {
        console.log("Connected to server!");
    };
    
    socket.onmessage = (event) => {
        try 
        {
            console.log("Receiving message data: ", event.data);

            // WebSocket messages are text (UTF-8 decoded by default)
            const data = JSON.parse(event.data);

            // Processing command messages
            if (typeof data.Command === "string")
            {
                // Commands?
            }

            // Validate required fields
            else if (typeof data.MemeName === "string" && typeof data.UserName === "string") 
            {
                const randomColor = nameToColor(data.UserName);

                // Putting a new meme in to the queue
                let qMeme = new queuedMeme(data.MemeName, data.UserName, randomColor);
                memeQueue.push(qMeme);
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
    if (memeQueue.length > 0 && !isMemePlaying)
    {
        meme = memeQueue.shift();

        playMeme(meme.memeName, meme.initiatorName, meme.nameColor);
    }

    else if (isMemeBoxShown && !isMemePlaying)
    {
        clearMeme();
    }
}

// PLAYS THE MEME!
async function playMeme(memeName, initiatorName, nameColor)
{
    // Update busy flag
    isMemePlaying = true;
    isMemeBoxShown = true;

    let imageFile = await findMemeImage(memeName);

    audioObj = await findMemeSound(memeName);

    let meme_box_1 = document.getElementById("meme_box_1");
    let meme_box_2 = document.getElementById("meme_box_2");

    // Choosing meme boxes
    let oldMemeBox = meme_box_1;
    let newMemeBox = meme_box_2;

    if (currentMemeBox)
    {
       oldMemeBox = meme_box_2;
       newMemeBox = meme_box_1;
    }

    currentMemeBox = !currentMemeBox;

    // Updating meme boxes

    newMemeBox.querySelector(".image").src = imageFile;
    newMemeBox.querySelector(".user_name").textContent = initiatorName;
    newMemeBox.querySelector(".user_name").style.color = nameColor;
    newMemeBox.querySelector(".meme_name").textContent = memeName;

    oldMemeBox.style.opacity = "0";
    newMemeBox.style.opacity = "1";

    const audioElem = newMemeBox.querySelector(".audio");
    audioElem.src = audioObj.src;

    let duration = audioObj.duration;
    audioElem.onerror = () => { duration = 2; }
    setTimeout( () => { isMemePlaying = false; }, duration * 1000);

    audioElem.play();
}

function clearMeme()
{
    isMemeBoxShown = false;

    let meme_boxes = Array(2);
    meme_boxes[0] = document.getElementById("meme_box_1");
    meme_boxes[1] = document.getElementById("meme_box_2");

    for (let i = 0; i < 2; i++)
    {
        meme_box = meme_boxes[i];

        meme_box.style.opacity = "0";
    }
}


async function findMemeImage(memeName)
{
    const formats = [".gif", ".png", ".jpeg", ".webp"];

    let fileBase = "../Data/" + memeName;

    let file = "";
    for (let i = 0; i < formats.length; i++)
    {
        file = fileBase + formats[i];

        let image = new Image();
        image.src = file;

        try
        {
            await image.decode();
            break;
        }

        catch {}
    }

    return file;
}

async function findMemeSound(memeName)
{
    const formats = [".mp3", ".wav"];

    let fileBase = "../Data/" + memeName;

    let file = "";
    for (let i = 0; i < formats.length; i++)
    {
        file = fileBase + formats[i];
        
        const audio = new Audio();
        audio.src = file;

        // Try to load audio
        const result = await new Promise((resolve) => {

            // Successfully loaded
            audio.addEventListener("canplaythrough", () => resolve(true), { once: true });

            // Failed to load
            audio.addEventListener("error", () => resolve(false), { once: true });
        });

        if (result)
        {
            return audio;
        }
    }

    return fileBase;
}

// Loads and decodes sound file 
async function loadSound(file) 
{
    const response = await fetch(file);
    const arrayBuffer = await response.arrayBuffer();
    return await ctx.decodeAudioData(arrayBuffer);
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
    const chatWindow = window.open(url, "MemeEffects", features);
}