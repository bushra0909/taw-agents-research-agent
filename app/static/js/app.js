
// ============================================
// RESEARCHIQ - COMPANY RESEARCH APPLICATION
// ============================================

document.addEventListener("DOMContentLoaded", () => {

    // 1. Get HTML elements
    const companyInput = document.getElementById("companyName");
    const researchBtn = document.getElementById("researchBtn");
    const buttonText = document.getElementById("buttonText");

    const loadingMessage = document.getElementById("loadingMessage");
    const errorMessage = document.getElementById("errorMessage");
    const successMessage = document.getElementById("successMessage");
    const downloadLink = document.getElementById("downloadLink");

    // Stop safely if an expected HTML element is missing.
    if (
        !companyInput ||
        !researchBtn ||
        !buttonText ||
        !loadingMessage ||
        !errorMessage ||
        !successMessage ||
        !downloadLink
    ) {
        console.error(
            "ResearchIQ could not find one or more required HTML elements."
        );
        return;
    }

    // Keep track of the current PDF download URL.
    let currentPdfUrl = null;


    // 2. Button click event
    researchBtn.addEventListener("click", generateResearch);


    // 3. Enter key event
    companyInput.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
            event.preventDefault();
            generateResearch();
        }
    });


    // 4. Main research function
    async function generateResearch() {

        const companyName = companyInput.value.trim();

        // Validate input.
        if (!companyName) {
            showError("Please enter a company name to begin.");
            companyInput.focus();
            return;
        }

        // Prevent multiple simultaneous requests.
        if (researchBtn.disabled) {
            return;
        }

        hideMessages();
        setLoading(true);

        try {

            // Send request to FastAPI.
            const response = await fetch("/research", {
                method: "POST",

                headers: {
                    "Content-Type": "application/json",
                    "Accept": "application/pdf"
                },

                body: JSON.stringify({
                    company_name: companyName
                })
            });

            // Handle backend errors.
            if (!response.ok) {

                let message = "Unable to generate your research brief.";

                try {
                    const errorData = await response.json();

                    if (errorData.detail) {
                        message = errorData.detail;
                    }

                } catch {
                    // Use the default error message.
                }

                throw new Error(message);
            }

            // Read the PDF returned by FastAPI.
            const pdfBlob = await response.blob();

            // Validate the PDF response.
            if (
                pdfBlob.size === 0 ||
                pdfBlob.type !== "application/pdf"
            ) {
                throw new Error(
                    "The server did not return a valid PDF. Please try again."
                );
            }

            // Remove the previous temporary download URL.
            if (currentPdfUrl) {
                URL.revokeObjectURL(currentPdfUrl);
            }

            // Create a new download URL.
            currentPdfUrl = URL.createObjectURL(pdfBlob);

            // Prepare a safe filename.
            const safeName = companyName
                .replace(/[^a-zA-Z0-9]+/g, "_")
                .replace(/^_+|_+$/g, "");

            // Connect the download button to the PDF.
            downloadLink.href = currentPdfUrl;
            downloadLink.download =
                `${safeName}_research_brief.pdf`;

            // Show successful result.
            successMessage.classList.remove("hidden");

            console.log(
                `Research completed successfully for ${companyName}.`
            );

        } catch (error) {

            console.error("ResearchIQ Error:", error);

            showError(
                error.message ||
                "Something went wrong. Please check your connection and try again."
            );

        } finally {

            // Always restore the button.
            setLoading(false);
        }
    }


    // 5. Loading state
    function setLoading(isLoading) {

        researchBtn.disabled = isLoading;
        companyInput.disabled = isLoading;

        if (isLoading) {

            buttonText.textContent = "Researching...";
            loadingMessage.classList.remove("hidden");

        } else {

            buttonText.textContent = "Generate Research Brief";
            loadingMessage.classList.add("hidden");

        }
    }


    // 6. Display error
    function showError(message) {

        errorMessage.textContent = message;
        errorMessage.classList.remove("hidden");

        successMessage.classList.add("hidden");
    }


    // 7. Hide old messages
    function hideMessages() {

        errorMessage.classList.add("hidden");
        successMessage.classList.add("hidden");
        loadingMessage.classList.add("hidden");
    }

});
