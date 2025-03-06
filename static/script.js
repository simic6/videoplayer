const videoPlayer = document.getElementById("videoPlayer");
const playPauseBtn = document.getElementById("playPauseBtn");
const restartBtn = document.getElementById("restartBtn");
const skipBackBtn = document.getElementById("skipBackBtn");
const skipForwardBtn = document.getElementById("skipForwardBtn");
const fileInput = document.getElementById("fileInput");
const downloadBtn = document.getElementById("downloadBtn");
const redFilterBtn = document.getElementById("redFilterBtn");
const greenFilterBtn = document.getElementById("greenFilterBtn");
const blueFilterBtn = document.getElementById("blueFilterBtn");
const applyFilterBtn = document.getElementById("applyFilterBtn");

let videoFileURL = ''; // Store the video file URL
let currentFilter = ''; // Store the selected filter

// Load the selected video file into the video player
fileInput.addEventListener("change", function() {
    const file = fileInput.files[0];
    if (file) {
        videoFileURL = URL.createObjectURL(file);
        const videoSource = document.getElementById("videoSource");
        videoSource.src = videoFileURL;
        videoPlayer.load();
        videoPlayer.play();
        playPauseBtn.textContent = "Pause"; // Change button to Pause
    }
});

// Play/Pause the video
playPauseBtn.addEventListener("click", function() {
    if (videoPlayer.paused) {
        videoPlayer.play();
        playPauseBtn.textContent = "Pause";
    } else {
        videoPlayer.pause();
        playPauseBtn.textContent = "Play";
    }
});

// Restart the video
restartBtn.addEventListener("click", function() {
    videoPlayer.currentTime = 0; // Go to the beginning
    videoPlayer.play(); // Start playing
    playPauseBtn.textContent = "Pause"; // Change button to Pause
});

// Skip back 5 seconds
skipBackBtn.addEventListener("click", function() {
    videoPlayer.currentTime -= 5;
});

// Skip forward 5 seconds
skipForwardBtn.addEventListener("click", function() {
    videoPlayer.currentTime += 5;
});

// Apply Red Filter
redFilterBtn.addEventListener("click", function() {
    videoPlayer.style.filter = 'sepia(100%) hue-rotate(-50deg)'; // A red filter
});

// Apply Green Filter
greenFilterBtn.addEventListener("click", function() {
    videoPlayer.style.filter = 'sepia(100%) hue-rotate(90deg)'; // A green filter
});

// Apply Blue Filter
blueFilterBtn.addEventListener("click", function() {
    videoPlayer.style.filter = 'sepia(100%) hue-rotate(180deg)'; // A blue filter
});

// Reset the filter
applyFilterBtn.addEventListener("click", function() {
    videoPlayer.style.filter = 'none'; // Remove any filters applied
});

document.getElementById("downloadLink").addEventListener("click", function(event) {
    // Add a slight delay before closing the tab
    setTimeout(function() {
        window.close();  // This will attempt to close the current tab
    }, 1000); // 1 second delay
});

const resetFilterBtn = document.getElementById("resetFilterBtn");

// Reset the filter
resetFilterBtn.addEventListener("click", function() {
    videoPlayer.style.filter = 'none'; // Remove any filters applied
});




