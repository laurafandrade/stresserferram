const passwordInput = document.getElementById('password');
const togglePassword = document.getElementById('togglePassword');

togglePassword.addEventListener('click', () => {
    const type = passwordInput.getAttribute('type');
    if (type === 'password') {
        passwordInput.setAttribute('type', 'text');
        togglePassword.setAttribute('src', '/static/eye-open.png');
    } else {
        passwordInput.setAttribute('type', 'password');
        togglePassword.setAttribute('src', '/static/eye-close.png');
    }
});
