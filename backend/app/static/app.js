// Сохраняем токен после логина (функция для будущей формы входа)
function saveToken(token) {
    localStorage.setItem('vk_manager_token', token);
}

// Получаем токен
function getToken() {
    return localStorage.getItem('vk_manager_token');
}

// Удаляем токен (выход)
function logout() {
    localStorage.removeItem('vk_manager_token');
    window.location.href = '/login';
}

// Автоматически добавляем токен ко всем fetch запросам
async function fetchWithAuth(url, options = {}) {
    const token = getToken();
    if (token) {
        options.headers = {
            ...options.headers,
            'Authorization': `Bearer ${token}`
        };
    }
    const response = await fetch(url, options);
    if (response.status === 401) {
        // Если токен протух — редирект на логин
        logout();
    }
    return response;
}