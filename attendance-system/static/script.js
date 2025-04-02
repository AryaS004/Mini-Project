document.addEventListener("DOMContentLoaded", function () {
    console.log("JavaScript Loaded!");

    // Image preview for signup
    const profileInput = document.getElementById("profile_image");
    const profilePreview = document.getElementById("profile_preview");

    if (profileInput && profilePreview) {
        profileInput.addEventListener("change", function (event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    profilePreview.src = e.target.result;
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // Delete user function in admin dashboard
    const deleteButtons = document.querySelectorAll(".delete-user");
    deleteButtons.forEach(button => {
        button.addEventListener("click", function () {
            const userId = this.dataset.id;
            fetch(`/delete_student/${userId}`, { method: "DELETE" })
                .then(response => response.json())
                .then(data => alert(data.message))
                .catch(error => alert("Error: " + error));
        });
    });
});
