const latitudeInput = document.getElementById("latitude")
const longitudeInput = document.getElementById("longitude")
const submitButton = document.getElementById("submit-button")
const loadingMessage = document.getElementById("loading-message")

function checkInputs() {
    if (latitudeInput.value && longitudeInput.value) {
        submitButton.disabled = false
    } else {
        submitButton.disabled = true
    }
}

function showLoadingMessage() {
    loadingMessage.style.display = "block"
}

function hideLoadingMessage() {
    loadingMessage.style.display = "none"
}

function successCallback(position) {
    latitudeInput.value = position.coords.latitude
    longitudeInput.value = position.coords.longitude
    hideLoadingMessage()
    checkInputs()
}

function errorCallback(error) {
    hideLoadingMessage()
    switch(error.code) {
        case error.PERMISSION_DENIED:
            alert("位置情報の取得がユーザーによって拒否されました。");
            break;
        case error.POSITION_UNAVAILABLE:
            alert("位置情報が利用できません。");
            break;
        case error.TIMEOUT:
            alert("タイムアウトしました。");
            break;
        case error.UNKNOWN_ERROR:
            alert("位置情報を取得できませんでした。");
            break;
    }
    alert("ページを更新してください。")
}

if (navigator.geolocation) {
    showLoadingMessage()
    navigator.geolocation.getCurrentPosition(successCallback, errorCallback)
} else {
    alert("この端末では位置情報が取得できません。")
}
