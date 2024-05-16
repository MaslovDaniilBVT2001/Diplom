function validateForm(event) {
    var firstName = document.getElementById("first_name").value;
    var lastName = document.getElementById("last_name").value;
    var username = document.getElementById("username").value;
    var password = document.getElementById("password").value;
    var email = document.getElementById("email").value;
    var role = document.getElementById("role").value;

    // Проверка наличия значений в обязательных полях
    if (!firstName || !lastName || !username || !password || !email || !role) {
        alert("Пожалуйста, заполните все поля формы.");
        event.preventDefault(); // Отменяем отправку формы
    }
}