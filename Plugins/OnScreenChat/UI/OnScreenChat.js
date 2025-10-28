
// Wait for the HTML file to be fully loaded before running the code
document.addEventListener("DOMContentLoaded", onFileLoaded);

function onFileLoaded()
{
    newMessage("AkarFire", "!Hello! everyone!", "rgba(255, 140, 0, 1)");
    newMessage("ae_Cookie", "hey", "rgba(255, 104, 227, 1)");
    newMessage("sbl", "!SIN!!SIN!!SIN!!SIN!!SIN!!SIN!!SIN!!SIN!!SIN!!SIN!!SIN!!SIN!!SIN!!SIN!!SIN!!SIN!!SIN!!SIN!", "rgb(104, 117, 255)");

    setInterval(() => {
    newMessage("ae_Cookie", "hey", "rgba(255, 104, 227, 1)");}, 1000);
}

function newMessage(user_name, message, user_color)
{
    let message_template = document.getElementById("message_template");
    let message_container = document.getElementById("message_container");

    let clone = message_template.content.cloneNode(true).querySelector(".message_div");

    // Customizing message
    let user_name_text = clone.querySelector(".user_name");
    let message_text = clone.querySelector(".message_text");

    user_name_text.textContent = user_name;
    message_text.textContent = message;

    user_name_text.style.color = user_color;
    
    // Appening message
    message_container.appendChild(clone);

    // Force reflow (forces browser to register current position/opacity)
    clone.offsetWidth; // reading this value triggers reflow

    requestAnimationFrame(() => { clone.classList.add("show"); });
}