// VendorBridge ERP Main JS

console.log("VendorBridge ERP Loaded");

// Auto hide messages after 3 seconds
setTimeout(() => {
    const messages = document.querySelectorAll(".message");

    messages.forEach(msg => {
        msg.style.display = "none";
    });

}, 3000);