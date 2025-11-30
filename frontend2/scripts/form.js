if (api.isAuthenticated()) {
    window.location.href = 'lkp.html';
}

let isRegisterMode = false;

// Переключение между входом и регистрацией
document.getElementById('toggleMode').addEventListener('click', function(e) {
    e.preventDefault();
    isRegisterMode = !isRegisterMode;

    const fullnameField = document.getElementById('fullname-field');
    const loginBtn = document.getElementById('loginBtn');
    const toggleLink = document.getElementById('toggleMode');

    if (isRegisterMode) {
        fullnameField.style.display = 'block';
        loginBtn.textContent = 'Зарегистрироваться';
        toggleLink.textContent = 'Уже есть аккаунт? Войти';
    } else {
        fullnameField.style.display = 'none';
        loginBtn.textContent = 'Войти';
        toggleLink.textContent = 'Нет аккаунта? Зарегистрироваться';
    }

    hideError();
});

// Кнопка сброса
let b = document.getElementById("b");
b.onclick = function(e) {
    e.preventDefault();
    document.querySelector("input#login").value = "";
    document.querySelector("input#password").value = "";
    document.querySelector("input#fullname").value = "";
    hideError();
}

// Кнопка входа/регистрации
let loginBtn = document.getElementById("loginBtn");
loginBtn.onclick = async function(e) {
    e.preventDefault();

    const email = document.getElementById("login").value.trim();
    const password = document.getElementById("password").value;
    const fullname = document.getElementById("fullname").value.trim();

    if (!email || !password) {
        showError("Введите email и пароль");
        return;
    }

    if (isRegisterMode && !fullname) {
        showError("Введите полное имя");
        return;
    }

    loginBtn.disabled = true;
    const originalText = loginBtn.textContent;
    loginBtn.textContent = isRegisterMode ? "Регистрация..." : "Вход...";

    try {
        if (isRegisterMode) {
            await api.register(email, password, fullname, 'teacher');
            showError("Регистрация успешна! Выполняется вход...");
            await api.login(email, password);
        } else {
            await api.login(email, password);
        }
        window.location.href = 'lkp.html';
    } catch (error) {
        const message = isRegisterMode
            ? "Ошибка регистрации. Возможно пользователь уже существует"
            : "Неверный email или пароль";
        showError(message);
        loginBtn.disabled = false;
        loginBtn.textContent = originalText;
    }
}

// Вход по Enter
document.getElementById("password").addEventListener("keypress", function(e) {
    if (e.key === "Enter") {
        loginBtn.click();
    }
});

function showError(message) {
    const errorDiv = document.getElementById("error-message");
    errorDiv.textContent = message;
    errorDiv.style.display = "block";
}

function hideError() {
    const errorDiv = document.getElementById("error-message");
    errorDiv.style.display = "none";
}