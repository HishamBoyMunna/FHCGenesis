window.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("loginForm");
    const signupForm = document.getElementById("signupForm");
    
    // Function to toggle between login and signup forms
    window.toggleForm = (type) => {
        if (type === "signup") {
            loginForm.classList.add("hidden");
            signupForm.classList.remove("hidden");
        } else {
            loginForm.classList.remove("hidden");
            signupForm.classList.add("hidden");
        }
    };

    // Function to toggle password visibility
    window.togglePassword = (inputId, checkboxId) => {
        const passwordInput = document.getElementById(inputId);
        const checkbox = document.getElementById(checkboxId);
        passwordInput.type = checkbox.checked ? "text" : "password";
    };

    // The code below for the growing tree animation is from your original file.
    // It's client-side and doesn't affect the form submission, so it can be kept as is.
    const trunk = document.querySelector("#growing-tree #tree-trunk");
    const leaves = document.querySelector("#growing-tree #tree-leaves");

    function updateTreeGrowth() {
        const activeForm = !loginForm.classList.contains("hidden") ? loginForm : signupForm;
        const inputs = activeForm.querySelectorAll('input[type="text"], input[type="email"], input[type="password"]');

        let totalLength = 0;
        inputs.forEach(input => {
            totalLength += input.value.length;
        });

        const maxLength = 40; // Max characters to reach full growth
        const growthFactor = Math.min(totalLength / maxLength, 1);
        
        const trunkScale = Math.min(0.1 + growthFactor * 0.9, 1);
        if (trunk) trunk.style.transform = `scaleY(${trunkScale})`;

        if (leaves) {
            if (growthFactor > 0.2) {
                const leavesScale = (growthFactor - 0.2) / 0.8;
                leaves.style.opacity = leavesScale;
                leaves.style.transform = `scale(${leavesScale})`;
            } else {
                leaves.style.opacity = 0;
                leaves.style.transform = `scale(0)`;
            }
        }
    }

    const allInputs = document.querySelectorAll('#loginForm input, #signupForm input');
    allInputs.forEach(input => {
        if (input.type !== "checkbox") {
             input.addEventListener("input", updateTreeGrowth);
        }
    });
    
    // Initial check
    updateTreeGrowth();
});