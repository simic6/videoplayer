const videoPlayer = document.getElementById("videoPlayer");
const playPauseBtn = document.getElementById("playPauseBtn");
const restartBtn = document.getElementById("restartBtn");
const skipBackBtn = document.getElementById("skipBackBtn");
const skipForwardBtn = document.getElementById("skipForwardBtn");
const fileInput = document.getElementById("fileInput");
const redFilterBtn = document.getElementById("redFilterBtn");
const greenFilterBtn = document.getElementById("greenFilterBtn");
const blueFilterBtn = document.getElementById("blueFilterBtn");
const pixelateBtn = document.getElementById("pixelateBtn");
const flipHBtn = document.getElementById("flipHBtn");
const flipVBtn = document.getElementById("flipVBtn");
const reverseBtn = document.getElementById("reverseBtn");
const resetColorFiltersBtn = document.getElementById("resetColorFiltersBtn");  // New reset button

let videoFileURL = ''; // Store the video file URL
let flipHorizontal = 1;  // Flip horizontal (1 = normal, -1 = flipped)
let flipVertical = 1;  // Flip vertical (1 = normal, -1 = flipped)
let rotation = 0;  // Keep track of the rotation
let currentFilter = ''; // Variable to keep track of the current filters
let reversePlayback = false; // Flag to track reverse mode
let pixelateActive = false;  // Track if pixelation is active

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
    if (reversePlayback) {
        // Prevent play/pause button from being used during reverse playback
        return;
    }

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

// Pixelate button functionality
pixelateBtn.addEventListener("click", function() {
    if (pixelateActive) {
        // Remove pixelation
        currentFilter = currentFilter.replace(' blur(10px)', '');
        pixelateBtn.textContent = "Pixelate";
        pixelateActive = false;
    } else {
        // Add pixelation
        currentFilter += ' blur(10px)';
        pixelateBtn.textContent = "Remove Pixelation";
        pixelateActive = true;
    }
    videoPlayer.style.filter = currentFilter.trim();
});

// Flip Horizontal
flipHBtn.addEventListener("click", function() {
    flipHorizontal *= -1;  // Toggle between 1 and -1
    applyTransform();
});

// Flip Vertical
flipVBtn.addEventListener("click", function() {
    flipVertical *= -1;  // Toggle between 1 and -1
    applyTransform();
});

// Apply the transformations to the video element
function applyTransform() {
    const transformString = `rotate(${rotation}deg) scaleX(${flipHorizontal}) scaleY(${flipVertical})`;
    videoPlayer.style.transform = transformString;
}

// Reverse playback button functionality
reverseBtn.addEventListener("click", function() {
    if (reversePlayback) {
        // Stop reverse playback
        reversePlayback = false;
        videoPlayer.play(); // Resume normal playback
        playPauseBtn.disabled = false; // Enable play button
        reverseBtn.textContent = "Reverse"; // Change button text back
    } else {
        // Start reverse playback
        reversePlayback = true;
        videoPlayer.pause(); // Pause the video
        playPauseBtn.disabled = true; // Disable play button while reversing
        reverseBtn.textContent = "Stop Reverse"; // Change button text
        reversePlaybackFunction(); // Start reverse function
    }
});

// Function to update the video player to play backwards
function reversePlaybackFunction() {
    if (reversePlayback && videoPlayer.currentTime > 0) {
        videoPlayer.currentTime -= 0.1; // Move backwards in time (0.1 seconds)
        setTimeout(reversePlaybackFunction, 100);  // Keep calling the function to keep playing backwards
    }
}

// Utility function to add a filter
function addFilter(newFilter) {
    if (!currentFilter.includes(newFilter)) {
        currentFilter += ` ${newFilter}`;
    }
}

// Utility function to remove a filter
function removeFilter(filterToRemove) {
    currentFilter = currentFilter.replace(new RegExp(`\\s*${filterToRemove}\\s*`, 'g'), '');
}

// Toggle Red Filter
redFilterBtn.addEventListener("click", function() {
    // Apply red filter
    removeFilter('sepia(100%) hue-rotate(90deg)');
    removeFilter('sepia(100%) hue-rotate(180deg)');
    addFilter('sepia(100%) hue-rotate(-50deg)');
    videoPlayer.style.filter = currentFilter.trim();
});

// Toggle Green Filter
greenFilterBtn.addEventListener("click", function() {
    // Apply green filter
    removeFilter('sepia(100%) hue-rotate(-50deg)');
    removeFilter('sepia(100%) hue-rotate(180deg)');
    addFilter('sepia(100%) hue-rotate(90deg)');
    videoPlayer.style.filter = currentFilter.trim();
});

// Toggle Blue Filter
blueFilterBtn.addEventListener("click", function() {
    // Apply blue filter
    removeFilter('sepia(100%) hue-rotate(-50deg)');
    removeFilter('sepia(100%) hue-rotate(90deg)');
    addFilter('sepia(100%) hue-rotate(180deg)');
    videoPlayer.style.filter = currentFilter.trim();
});



const removeColorFilterBtn = document.getElementById("removeColorFilterBtn");

// Reset all color filters
removeColorFilterBtn.addEventListener("click", function() {
    // Remove all color filters by clearing the `currentFilter`
    currentFilter = currentFilter.replace(/(sepia\(100%\) hue-rotate\([-\d\.]+deg\))+/g, '');
    videoPlayer.style.filter = currentFilter.trim(); // Apply the updated filter
    // Update button text
    removeColorFilterBtn.textContent = "Color Filter Remove";
});

const blackBorderBtn = document.getElementById("blackBorderBtn");
let blackBorderActive = false;  // Flag to track whether the black border is applied

// Add/Remove Black Border
blackBorderBtn.addEventListener("click", function() {
    if (blackBorderActive) {
        // Remove black border
        videoPlayer.style.border = "none";
        blackBorderBtn.textContent = "Add Black Border"; // Change button text
    } else {
        // Add black border
        videoPlayer.style.border = "10px solid black"; // Add a black border
        blackBorderBtn.textContent = "Remove  Border"; // Change button text
    }
    blackBorderActive = !blackBorderActive; // Toggle black border state
});



       


