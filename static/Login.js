function generateCaptcha() {
    let characters ='ABCDEFGHJKLMNOPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz0123456789';
    let captcha = '';
    for(let i=0; i<6; i++) {
        let char = characters.charAt(Math.floor(Math.random() * characters.length));
        captcha += char;
    }
    return captcha;
}

function refresh() {
    let captcha = generateCaptcha();
    document.getElementById('cap').innerText = captcha;
}

document.getElementById('cap').innerText = generateCaptcha();

function validateForm() {
    var captchacode = document.getElementById("captchacode").value;
    var generatedCaptcha = document.getElementById("cap").innerText.trim();  // Trim to remove any leading/trailing whitespace
    if (captchacode.toLowerCase() === generatedCaptcha.toLowerCase()) {  // Use toLowerCase for case-insensitive comparison
        
        return true;
    } else {
        alert("Incorrect CAPTCHA code. Please try again.");
        return false;
    }
}
