document.getElementById('forgot-password-form').addEventListener('submit', function(event) {
    event.preventDefault();
    // Send student code and date of birth to server and receive OTP
    var studentCode = document.getElementById('student_code').value;
    var dob = document.getElementById('dob').value;

    // Example AJAX request (you can use fetch or any library like Axios)
    fetch('/send_otp', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ student_code: studentCode, dob: dob })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Hide the forgot password form and show OTP form
            document.getElementById('forgot-password-form').style.display = 'none';
            document.getElementById('otp-section').style.display = 'block';
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});
