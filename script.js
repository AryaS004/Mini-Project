const body=document.querySelector("body"),
 sidebar=body.querySelector(".sidebar"),
toggle=body.querySelector(".toggle"),
searchBtn=body.querySelector(".search-box"),
modeSwitch=body.querySelector(".toggle-switch"),
modeText=body.querySelector(".mode-text")

modeSwitch.addEventListener("click",()=>{
    body.classList.toggle("dark");
    if(body.classList.contains("dark")){
        modeText.innerText="Light Mode";
    }
    else{
        modeText.innerText="Dark Mode";
    }
});
toggle.addEventListener("click",()=>{
    sidebar.classList.toggle("close");
});

document.addEventListener("DOMContentLoaded", function() {
    let attendanceBtn = document.getElementById("attendance-btn");
    let submenu = document.getElementById("attendance-submenu");

    submenu.style.display = "none";

    attendanceBtn.addEventListener("click", function(event) {
        event.preventDefault(); // Prevent default link action
        submenu.style.display = submenu.style.display === "block" ? "none" : "block";
    });
});






    document.addEventListener("DOMContentLoaded", function () {
        const logoutBtn = document.getElementById("logout-btn");

        if (logoutBtn) {
            logoutBtn.addEventListener("click", function (event) {
                event.preventDefault(); // Prevent default link behavior

                // Clear session storage or local storage (depending on how you handle authentication)
                sessionStorage.clear();  // If using session storage
                localStorage.clear();    // If using local storage

                alert("Logged out successfully!");

                // Redirect to login page or home page
                window.location.href = "studentlogin.html";
            });
        } else {
            console.error("Logout button not found!");
        }
    });



// Dynamic Greeting based on time of day
const greetingElement = document.getElementById("greeting");
const dateTimeElement = document.getElementById("date-time");
const attendanceProgress = document.getElementById("attendance-progress");
const scheduleList = document.getElementById("schedule-list");
const assignmentsList = document.getElementById("assignments-list");

// Get the current date and time
function updateDateTime() {
    const now = new Date();
    const hours = now.getHours();
    const minutes = now.getMinutes();
    const seconds = now.getSeconds();
    const day = now.toLocaleDateString();

    // Format time as HH:MM:SS
    const formattedTime = `${hours < 10 ? '0' + hours : hours}:${minutes < 10 ? '0' + minutes : minutes}:${seconds < 10 ? '0' + seconds : seconds}`;
    
    dateTimeElement.textContent = `${day} - ${formattedTime}`;
}

// Update greeting based on time of day
function updateGreeting() {
    const now = new Date();
    const hours = now.getHours();
    let greeting = "Good Morning, Student!";

    if (hours >= 12 && hours < 18) {
        greeting = "Good Afternoon, Student!";
    } else if (hours >= 18) {
        greeting = "Good Evening, Student!";
    }

    greetingElement.textContent = greeting;
}

// Attendance percentage (use actual data in real implementation)
function updateAttendanceProgress() {
    const attendance = 85; // Example: 85% attendance
    document.documentElement.style.setProperty('--attendance', attendance);
    document.getElementById('attendance-percentage').textContent = `${attendance}%`;
}

// Load daily schedule
function loadSchedule() {
    const schedule = [
        "Math - 9:00 AM",
        "English - 11:00 AM",
        "History - 1:00 PM",
        "Computer Science - 3:00 PM"
    ];

    schedule.forEach(item => {
        const li = document.createElement("li");
        li.textContent = item;
        scheduleList.appendChild(li);
    });
}

// Load upcoming assignments
function loadAssignments() {
    const assignments = [
        "Math Homework - Due Feb 20th",
        "Science Project - Due Feb 25th",
        "History Essay - Due March 1st"
    ];

    assignments.forEach(item => {
        const li = document.createElement("li");
        li.textContent = item;
        assignmentsList.appendChild(li);
    });
}

// Initial setup
function initDashboard() {
    updateGreeting();
    updateDateTime();
    updateAttendanceProgress();
    loadSchedule();
    loadAssignments();
    setInterval(updateDateTime, 1000);  // Update time every second
}

initDashboard();



