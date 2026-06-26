// =====================================================
// DocMind AI
// Professional Frontend
// Version 2.0
// =====================================================

// =====================================================
// DOM ELEMENTS
// =====================================================

const uploadBtn = document.getElementById("uploadBtn");
const askBtn = document.getElementById("askBtn");

const pdfFile = document.getElementById("pdfFile");
const uploadStatus = document.getElementById("uploadStatus");

const questionInput = document.getElementById("question");

const chatWindow = document.getElementById("chatWindow");

const pdfList = document.getElementById("pdfList");

const storageText = document.getElementById("storageText");

const storageFill = document.querySelector(".storage-fill");

const chatHistory = document.getElementById("chatHistory");

// =====================================================
// APP STATE
// =====================================================

let uploadedPDFs = [];

let isUploading = false;

let isThinking = false;

// =====================================================
// INITIALIZATION
// =====================================================

window.addEventListener("DOMContentLoaded", () => {

    questionInput.focus();

});

// =====================================================
// EVENT LISTENERS
// =====================================================

uploadBtn.addEventListener("click", uploadPDF);

askBtn.addEventListener("click", askQuestion);

questionInput.addEventListener("keydown", function (e) {

    if (e.key === "Enter" && !e.shiftKey) {

        e.preventDefault();

        askQuestion();

    }

});

// =====================================================
// BUTTON HELPERS
// =====================================================

function disableButton(button, text) {

    button.disabled = true;

    button.innerText = text;

}

function enableButton(button, text) {

    button.disabled = false;

    button.innerText = text;

}

// =====================================================
// ESCAPE HTML
// =====================================================

function escapeHTML(text) {

    const div = document.createElement("div");

    div.innerText = text;

    return div.innerHTML;

}

// =====================================================
// UPLOAD PDFs
// =====================================================

async function uploadPDF() {

    if (isUploading) return;

    const files = pdfFile.files;

    if (files.length === 0) {

        alert("Please choose one or more PDF files.");

        return;

    }

    isUploading = true;

    disableButton(uploadBtn, "Uploading...");

    uploadStatus.innerHTML = `Uploading ${files.length} PDF(s)...`;

    for (const file of files) {

        const formData = new FormData();

        formData.append("file", file);

        try {

            const response = await fetch("/upload", {

                method: "POST",

                body: formData

            });

            const data = await response.json();

            if (data.error) {

                uploadStatus.innerHTML = "❌ " + data.error;

            }

            else {

                addPDF(file.name);

                uploadStatus.innerHTML =
                    "✅ Upload completed successfully.";

            }

        }

        catch (error) {

            console.error(error);

            uploadStatus.innerHTML =
                "❌ Cannot connect to Flask server.";

        }

    }

    pdfFile.value = "";

    enableButton(uploadBtn, "Upload");

    isUploading = false;

}

// =====================================================
// ASK QUESTION
// =====================================================

async function askQuestion() {

    if (isThinking) return;

    const question = questionInput.value.trim();

    if (question === "") return;

    isThinking = true;

    disableButton(askBtn, "Thinking...");

    addUserMessage(question);

    addChatHistory(question);

    questionInput.value = "";

    showThinking();

    try {

        const response = await fetch("/ask", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                question: question
            })

        });

        const data = await response.json();

        removeThinking();

        if (data.error) {

            addAIMessage("❌ " + data.error);

        } else {

            addAIMessage(data.answer);

        }

    }

    catch (error) {

        console.error(error);

        removeThinking();

        addAIMessage("❌ Unable to connect to the backend.");

    }

    enableButton(askBtn, "Send");

    isThinking = false;

    questionInput.focus();

}

// =====================================================
// USER MESSAGE
// =====================================================

function addUserMessage(message) {

    const html = `

    <div class="message user-message">

        <div class="bubble user">

            ${escapeHTML(message)}

        </div>

    </div>

    `;

    chatWindow.insertAdjacentHTML("beforeend", html);

    scrollBottom();

}

// =====================================================
// AI MESSAGE
// =====================================================

function addAIMessage(message) {

    const html = `

    <div class="message ai-message">

        <div class="bubble ai">

            <strong>🤖 DocMind AI</strong>

            <hr>

            ${escapeHTML(message).replace(/\n/g,"<br>")}

        </div>

    </div>

    `;

    chatWindow.insertAdjacentHTML("beforeend", html);

    scrollBottom();

}

// =====================================================
// THINKING MESSAGE
// =====================================================

function showThinking() {

    const html = `

    <div class="message ai-message"

         id="thinking">

        <div class="bubble ai">

            🤖 Thinking...

        </div>

    </div>

    `;

    chatWindow.insertAdjacentHTML("beforeend", html);

    scrollBottom();

}

function removeThinking() {

    const thinking = document.getElementById("thinking");

    if (thinking) {

        thinking.remove();

    }

}

// =====================================================
// PDF SIDEBAR
// =====================================================

function addPDF(filename) {

    if (uploadedPDFs.includes(filename)) {

        return;

    }

    uploadedPDFs.push(filename);

    pdfList.innerHTML = "";

    uploadedPDFs.forEach(pdf => {

        const html = `

        <div class="pdf-item">

            📄 ${escapeHTML(pdf)}

        </div>

        `;

        pdfList.insertAdjacentHTML("beforeend", html);

    });

    updateStorage();

}

// =====================================================
// STORAGE
// =====================================================

function updateStorage() {

    storageText.innerText =
        `${uploadedPDFs.length} PDF(s) Loaded`;

    const percentage =
        Math.min(uploadedPDFs.length * 10, 100);

    storageFill.style.width =
        percentage + "%";

}

// =====================================================
// CHAT HISTORY
// =====================================================

function addChatHistory(question) {

    if (chatHistory.querySelector(".empty")) {

        chatHistory.innerHTML = "";

    }

    const shortQuestion =

        question.length > 35

        ? question.substring(0,35) + "..."

        : question;

    const html = `

    <div class="history-item">

        💬 ${escapeHTML(shortQuestion)}

    </div>

    `;

    chatHistory.insertAdjacentHTML("beforeend", html);

}

// =====================================================
// AUTO SCROLL
// =====================================================

function scrollBottom() {

    chatWindow.scrollTo({

        top: chatWindow.scrollHeight,

        behavior: "smooth"

    });

}

// =====================================================
// HELPER
// =====================================================

function clearChat() {

    chatWindow.innerHTML = "";

}

console.log("✅ DocMind AI Frontend Loaded Successfully");