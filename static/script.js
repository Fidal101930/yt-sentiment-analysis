let pieChart = null;
let gaugeChart = null;


// ======================================================
// ANALYZE VIDEO
// ======================================================

async function analyzeVideo() {

    const videoUrl = document.getElementById("video_url").value.trim();

    if (!videoUrl) {
        showToast("Please enter a YouTube URL.");
        return;
    }

    const loading = document.getElementById("loading");

    loading.style.display = "block";

    console.log("1. Sending URL:", videoUrl);

    try {

        const response = await fetch("/analyze", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                video_url: videoUrl
            })
        });

        console.log("2. HTTP status:", response.status);

        // Read the response as text FIRST.
        // This lets us see Flask errors even when it doesn't return JSON.
        const responseText = await response.text();

        console.log("3. Raw server response:", responseText);

        let data;

        try {
            data = JSON.parse(responseText);
        }
        catch (jsonError) {
            throw new Error(
                "Flask returned non-JSON response: " +
                responseText.substring(0, 300)
            );
        }

        console.log("4. Parsed response:", data);

        if (!response.ok) {
            throw new Error(
                data.error || `Server returned ${response.status}`
            );
        }

        if (data.error) {
            throw new Error(data.error);
        }

        // -----------------------------
        // VIDEO DETAILS
        // -----------------------------

        if (data.video) {

            document.getElementById("title").textContent =
                data.video.title || "Unknown title";

            document.getElementById("channel").textContent =
                data.video.channel || "Unknown channel";

            document.getElementById("views").textContent =
                "Views: " +
                Number(data.video.views || 0).toLocaleString();

            const thumbnail =
                document.getElementById("thumbnail");

            if (data.video.thumbnail) {
                thumbnail.src = data.video.thumbnail;
                thumbnail.style.display = "block";
            }
        }
        else {
            console.warn("No video object returned.");
        }

        // -----------------------------
        // COUNTS
        // -----------------------------

        const total = Number(data.total_comments || 0);
        const positive = Number(data.positive || 0);
        const neutral = Number(data.neutral || 0);
        const negative = Number(data.negative || 0);

        document.getElementById("total").textContent = total;
        document.getElementById("positive").textContent = positive;
        document.getElementById("neutral").textContent = neutral;
        document.getElementById("negative").textContent = negative;

        // -----------------------------
        // SCORE
        // -----------------------------

        const score =
            total > 0
                ? Math.round((positive / total) * 100)
                : 0;

        document.getElementById("score").textContent =
            score + "%";

        // -----------------------------
        // CHARTS
        // -----------------------------

        createPieChart(
            positive,
            neutral,
            negative
        );

        createGaugeChart(score);

        // -----------------------------
        // COMMENTS
        // -----------------------------

        displayComments(
            data.comments || []
        );

        showToast("Analysis completed successfully.");

    }
    catch (error) {

        console.error(
            "ANALYZE ERROR:",
            error
        );

        showToast(
            error.message
        );

    }
    finally {

        loading.style.display = "none";

    }
}


// ======================================================
// PIE CHART
// ======================================================

function createPieChart(positive, neutral, negative) {

    const canvas = document.getElementById("pieChart");

    if (!canvas) {
        return;
    }

    const total = positive + neutral + negative;

    // Don't create an empty chart
    if (total === 0) {

        if (pieChart) {
            pieChart.destroy();
            pieChart = null;
        }

        return;
    }

    if (pieChart) {
        pieChart.destroy();
    }

    pieChart = new Chart(canvas, {

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
                    "#facc15",
                    "#ef4444"
                ],

                borderWidth: 0

            }]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            plugins: {

                legend: {
                    position: "bottom"
                }

            }

        }

    });
}
// ======================================================
// GAUGE CHART
// ======================================================

function createGaugeChart(score) {

    const canvas =
        document.getElementById("gaugeChart");

    if (!canvas) {
        return;
    }


    if (gaugeChart) {
        gaugeChart.destroy();
    }


    gaugeChart = new Chart(
        canvas,
        {

            type: "doughnut",

            data: {

                labels: [
                    "Score",
                    "Remaining"
                ],

                datasets: [

                    {

                        data: [
                            score,
                            100 - score
                        ]

                    }

                ]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                circumference: 180,

                rotation: -90,

                plugins: {

                    legend: {
                        display: false
                    }

                }

            }

        }
    );

}


// ======================================================
// DISPLAY COMMENTS
// ======================================================

// ======================================================
// DISPLAY COMMENTS
// ======================================================

function displayComments(comments) {

    const container = document.getElementById("comments");

    if (!container) {
        return;
    }

    container.innerHTML = "";

    if (!Array.isArray(comments) || comments.length === 0) {

        container.innerHTML = `
            <div class="comment">
                <p>No comments available.</p>
            </div>
        `;

        return;
    }

    comments.forEach((item, index) => {

        const commentText =
            String(item.comment ?? "");

        const sentiment =
            String(item.sentiment ?? "Unclassified")
                .trim();

        const sentimentClass =
            sentiment.toLowerCase();

        let icon = "😐";

        if (sentimentClass === "positive") {
            icon = "😊";
        } else if (sentimentClass === "negative") {
            icon = "😞";
        } else if (sentimentClass === "neutral") {
            icon = "😐";
        } else {
            icon = "❓";
        }

        const commentDiv =
            document.createElement("div");

        commentDiv.className = "comment";

        commentDiv.innerHTML = `
            <div class="comment-header">

                <span class="badge ${sentimentClass}">
                    ${icon} ${escapeHTML(sentiment)}
                </span>

                <span>#${index + 1}</span>

            </div>

            <p>${escapeHTML(commentText)}</p>
        `;

        container.appendChild(commentDiv);
    });
}


// ======================================================
// SENTIMENT ICON
// ======================================================

function getSentimentIcon(sentiment) {

    const value =
        String(sentiment).toLowerCase();

    if (value === "positive") {
        return "😊";
    }

    if (value === "negative") {
        return "😞";
    }

    return "😐";
}


// ======================================================
// ESCAPE HTML
// ======================================================

function escapeHTML(text) {

    const div = document.createElement("div");

    div.textContent = text;

    return div.innerHTML;
}


// ======================================================
// SEARCH COMMENTS
// ======================================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        const search =
            document.getElementById(
                "searchComment"
            );


        if (!search) {
            return;
        }


        search.addEventListener(
            "input",
            function () {

                const query =
                    search.value.toLowerCase();


                const comments =
                    document.querySelectorAll(
                        ".comment-item"
                    );


                comments.forEach(
                    comment => {

                        const text =
                            comment.textContent
                            .toLowerCase();


                        if (
                            text.includes(query)
                        ) {

                            comment.style.display =
                                "block";

                        }

                        else {

                            comment.style.display =
                                "none";

                        }

                    }
                );

            }
        );

    }
);


// ======================================================
// TOAST
// ======================================================

function showToast(message) {

    const toast =
        document.getElementById("toast");


    if (!toast) {
        alert(message);
        return;
    }


    toast.textContent =
        message;


    toast.classList.add("show");


    setTimeout(
        function () {

            toast.classList.remove(
                "show"
            );

        },
        3000
    );

}