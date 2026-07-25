// =============================================
// YouTube Sentiment Dashboard
// script.js - Part 4A
// =============================================

// Global Variables

let pieChart = null;
let gaugeChart = null;
let commentsData = [];

// =============================================
// Analyze Video
// =============================================

async function analyzeVideo() {

    const url = document.getElementById("video_url").value.trim();

    if (url === "") {

        showToast("Please enter a YouTube URL.");

        return;
    }

    document.getElementById("loading").style.display = "block";

    try {

        const response = await fetch("/analyze", {

            method: "POST",

            headers: {

                "Content-Type": "application/json"

            },

            body: JSON.stringify({

                video_url: url

            })

        });

        const data = await response.json();

        document.getElementById("loading").style.display = "none";

        if (data.error) {

            showToast(data.error);

            return;
        }

        updateDashboard(data);

    }

    catch (error) {

        document.getElementById("loading").style.display = "none";

        console.error(error);

        showToast("Unable to connect to Flask server.");

    }

}

// =============================================
// Update Dashboard
// =============================================

function updateDashboard(data) {

    animateCounter("total", data.total_comments);

    animateCounter("positive", data.positive);

    animateCounter("neutral", data.neutral);

    animateCounter("negative", data.negative);

    // Video Information

    if (data.thumbnail)
        document.getElementById("thumbnail").src = data.thumbnail;

    if (data.title)
        document.getElementById("title").innerHTML = data.title;

    if (data.channel)
        document.getElementById("channel").innerHTML =
            "Channel : " + data.channel;

    if (data.views)
        document.getElementById("views").innerHTML =
            "Views : " + Number(data.views).toLocaleString();

    commentsData = data.comments;

    createPieChart(

        data.positive,

        data.neutral,

        data.negative

    );

    createGauge(

        data.positive,

        data.total_comments

    );

    displayComments(commentsData);

}

// =============================================
// Animated Counter
// =============================================

function animateCounter(id, value) {

    const element = document.getElementById(id);

    let start = 0;

    const duration = 1200;

    const increment = value / (duration / 20);

    const timer = setInterval(() => {

        start += increment;

        if (start >= value) {

            start = value;

            clearInterval(timer);

        }

        element.innerHTML = Math.floor(start);

    }, 20);

}

// =============================================
// Search Comments
// =============================================

document.getElementById("searchComment").addEventListener(

    "keyup",

    function () {

        const keyword = this.value.toLowerCase();

        const filtered = commentsData.filter(comment =>

            comment.Comment.toLowerCase().includes(keyword)

        );

        displayComments(filtered);

    }

);

// =============================================
// Toast Notification
// =============================================

function showToast(message) {

    const toast = document.getElementById("toast");

    toast.innerHTML = message;

    toast.classList.add("show");

    setTimeout(() => {

        toast.classList.remove("show");

    }, 3000);

}

// =============================================
// Pie Chart
// =============================================

function createPieChart(positive, neutral, negative) {

    const ctx = document.getElementById("pieChart").getContext("2d");

    if (pieChart) {
        pieChart.destroy();
    }

    pieChart = new Chart(ctx, {

        type: "doughnut",

        data: {

            labels: [

                "Positive",

                "Neutral",

                "Negative"

            ],

            datasets: [{

                data: [

                    positive,

                    neutral,

                    negative

                ],

                backgroundColor: [

                    "#22c55e",

                    "#f59e0b",

                    "#ef4444"

                ],

                borderColor: [

                    "#22c55e",

                    "#f59e0b",

                    "#ef4444"

                ],

                borderWidth: 2,

                hoverOffset: 18

            }]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            cutout: "65%",

            plugins: {

                legend: {

                    position: "bottom",

                    labels: {

                        color: "#ffffff",

                        padding: 20,

                        font: {

                            size: 14,

                            weight: "bold"

                        }

                    }

                }

            },

            animation: {

                animateRotate: true,

                duration: 1500

            }

        }

    });

}

// =============================================
// Gauge Chart
// =============================================

function createGauge(positive, total) {

    const score = total === 0

        ? 0

        : Math.round((positive / total) * 100);

    document.getElementById("score").innerHTML = score + "%";

    const ctx = document.getElementById("gaugeChart").getContext("2d");

    if (gaugeChart) {
        gaugeChart.destroy();
    }

    let gaugeColor = "#22c55e";

    if (score < 75)
        gaugeColor = "#f59e0b";

    if (score < 45)
        gaugeColor = "#ef4444";

    gaugeChart = new Chart(ctx, {

        type: "doughnut",

        data: {

            datasets: [{

                data: [

                    score,

                    100 - score

                ],

                backgroundColor: [

                    gaugeColor,

                    "#273549"

                ],

                borderWidth: 0

            }]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            rotation: -90,

            circumference: 180,

            cutout: "78%",

            plugins: {

                legend: {

                    display: false

                },

                tooltip: {

                    enabled: false

                }

            },

            animation: {

                duration: 1800,

                easing: "easeOutBounce"

            }

        }

    });

}

// =============================================
// Dashboard Entrance Animation
// =============================================

function animateCards() {

    const cards = document.querySelectorAll(

        ".glass-card, .stat-card"

    );

    cards.forEach((card, index) => {

        card.style.opacity = "0";

        card.style.transform = "translateY(30px)";

        setTimeout(() => {

            card.style.transition = "0.6s ease";

            card.style.opacity = "1";

            card.style.transform = "translateY(0)";

        }, index * 100);

    });

}

window.addEventListener("load", animateCards);

// =============================================
// Display Comments
// =============================================

function displayComments(comments) {

    const container = document.getElementById("comments");

    container.innerHTML = "";

    if (comments.length === 0) {

        container.innerHTML = `
            <div class="comment">
                <p>No comments found.</p>
            </div>
        `;

        return;
    }

    comments.forEach((item, index) => {

        const sentiment = item.Sentiment.toLowerCase();

        const icon = sentiment === "positive"
            ? "😊"
            : sentiment === "neutral"
            ? "😐"
            : "😞";

        container.innerHTML += `

            <div class="comment fadeIn">

                <div class="comment-header">

                    <span class="badge ${sentiment}">
                        ${icon} ${item.Sentiment}
                    </span>

                    <span>#${index + 1}</span>

                </div>

                <p>

                    ${item.Comment}

                </p>

            </div>

        `;

    });

}

// =============================================
// Press ENTER to Analyze
// =============================================

document
.getElementById("video_url")
.addEventListener("keypress", function(e){

    if(e.key === "Enter"){

        analyzeVideo();

    }

});

// =============================================
// Clear Search
// =============================================

function clearSearch(){

    document.getElementById("searchComment").value="";

    displayComments(commentsData);

}

// =============================================
// Export Comments as CSV
// =============================================

function exportCSV(){

    if(commentsData.length===0){

        showToast("Nothing to export.");

        return;

    }

    let csv="Sentiment,Comment\n";

    commentsData.forEach(item=>{

        let comment=item.Comment.replace(/"/g,'""');

        csv+=`${item.Sentiment},"${comment}"\n`;

    });

    const blob=new Blob([csv],{

        type:"text/csv"

    });

    const url=window.URL.createObjectURL(blob);

    const a=document.createElement("a");

    a.href=url;

    a.download="youtube_sentiment.csv";

    document.body.appendChild(a);

    a.click();

    document.body.removeChild(a);

}

// =============================================
// Copy Results
// =============================================

function copySummary(){

    const text=

`YouTube Sentiment Analysis

Total Comments : ${document.getElementById("total").innerText}

Positive : ${document.getElementById("positive").innerText}

Neutral : ${document.getElementById("neutral").innerText}

Negative : ${document.getElementById("negative").innerText}

Overall Score : ${document.getElementById("score").innerText}`;

    navigator.clipboard.writeText(text);

    showToast("Summary copied.");

}

// =============================================
// Auto Scroll
// =============================================

function scrollToComments(){

    document.getElementById("comments")

    .scrollIntoView({

        behavior:"smooth"

    });

}

// =============================================
// Dashboard Reset
// =============================================

function resetDashboard(){

    document.getElementById("total").innerHTML="0";

    document.getElementById("positive").innerHTML="0";

    document.getElementById("neutral").innerHTML="0";

    document.getElementById("negative").innerHTML="0";

    document.getElementById("score").innerHTML="0%";

    document.getElementById("comments").innerHTML="";

    document.getElementById("thumbnail").src="";

    document.getElementById("title").innerHTML="Video Title";

    document.getElementById("channel").innerHTML="";

    document.getElementById("views").innerHTML="";

    if(pieChart){

        pieChart.destroy();

        pieChart=null;

    }

    if(gaugeChart){

        gaugeChart.destroy();

        gaugeChart=null;

    }

}

// =============================================
// Welcome Message
// =============================================

window.onload=function(){

    animateCards();

    showToast("Welcome to YouTube Sentiment Dashboard 🚀");

};

// =============================
// Install PWA
// =============================

let deferredPrompt;

const installBtn = document.getElementById("installBtn");

window.addEventListener("beforeinstallprompt", (e) => {

    e.preventDefault();

    deferredPrompt = e;

    if (installBtn) {
        installBtn.style.display = "inline-flex";
    }

});

if (installBtn) {

    installBtn.addEventListener("click", async () => {

        installBtn.style.display = "none";

        deferredPrompt.prompt();

        const { outcome } = await deferredPrompt.userChoice;

        console.log("Install:", outcome);

        deferredPrompt = null;

    });

}