function successCallback(position) {
    const latitude = position.coords.latitude
    const longitude = position.coords.longitude
    document.getElementById("latitude").value = latitude
    document.getElementById("longitude").value = longitude
}

function errorCallback(error) {
    alert("位置情報が取得できませんでした。")
    console.log(error)
}

if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(successCallback, errorCallback)
} else {
    alert("この端末では位置情報が取得できません。")
}
