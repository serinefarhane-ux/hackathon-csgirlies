const form = document.getElementById("subscribeForm");
const emailInput = document.getElementById("email");
const message = document.getElementById("message");

form.addEventListener("submit", async function (event) {
    event.preventDefault();

    const email = emailInput.value.trim();

    if (!email) {
        message.textContent = "Please enter your email.";
        return;
    }

    message.textContent = "Subscribing...";

    try {
        const response = await fetch("/subscribe", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                email: email
            })
        });

        const data = await response.json();

        message.textContent = data.message;

        if (data.success) {
            emailInput.value = "";
        }

    } catch (error) {
        console.error(error);
        message.textContent = "Something went wrong. Please try again.";
    }
});
