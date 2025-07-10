window.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("loginForm");
    const signupForm = document.getElementById("signupForm");
    const trunk = document.getElementById("tree-trunk");
    const leaves = document.getElementById("tree-leaves");

    const allInputs = [
        ...document.querySelectorAll("#loginForm input"),
        ...document.querySelectorAll("#signupForm input")
    ];

    // Function to toggle between login and signup forms
    window.toggleForm = (type) => {
        if (type === "signup") {
            loginForm.classList.add("hidden");
            signupForm.classList.remove("hidden");
        } else {
            signupForm.classList.add("hidden");
            loginForm.classList.remove("hidden");
        }
        updateTreeGrowth(); // Update tree on form toggle
    };

    // Function to toggle password visibility
    window.togglePassword = (inputId, checkboxId) => {
        const passwordInput = document.getElementById(inputId);
        const checkbox = document.getElementById(checkboxId);
        passwordInput.type = checkbox.checked ? "text" : "password";
    };

    // Handle form submissions
    loginForm.addEventListener("submit", (e) => {
        e.preventDefault();
        alert("Login successful! 🌿");
    });

    signupForm.addEventListener("submit", (e) => {
        e.preventDefault();
        alert("Signup successful! 🌱");
    });

    // Function to update the tree's growth based on input length
    function updateTreeGrowth() {
        const activeForm = !loginForm.classList.contains("hidden") ? loginForm : signupForm;
        const inputs = activeForm.querySelectorAll('input[type="text"], input[type="email"], input[type="password"]');

        let totalLength = 0;
        inputs.forEach(input => {
            totalLength += input.value.length;
        });

        const maxLength = 40; // Max characters to reach full growth
        const growthFactor = Math.min(totalLength / maxLength, 1);

        // Grow the trunk first, then the leaves
        const trunkScale = Math.min(0.1 + growthFactor * 0.9, 1);
        trunk.style.transform = `scaleY(${trunkScale})`;

        // Leaves start growing after trunk is partially grown
        if (growthFactor > 0.2) {
            const leavesScale = (growthFactor - 0.2) / 0.8;
            leaves.style.opacity = leavesScale;
            leaves.style.transform = `scale(${leavesScale})`;
        } else {
            leaves.style.opacity = 0;
            leaves.style.transform = `scale(0)`;
        }
    }

    // Add input event listeners to all text/email/password fields
    allInputs.forEach(input => {
        if (input.type !== "checkbox") {
             input.addEventListener("input", updateTreeGrowth);
        }
    });

    // Initial check in case of browser auto-fill
    updateTreeGrowth();
});
