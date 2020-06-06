function toggleStore() {
	var ele = document.getElementsByName('store');
	var i, store, google, apple;
	for (i = 0; i < ele.length; i++) {
		if (ele[i].checked) {
			store = ele[i].id;
			google = document.getElementById("playStoreInput");
			apple = document.getElementById("appStoreInput");
			if (store == "playStore") {
				google.style.display = "block";
				apple.style.display = "none";
				document.getElementById("package_name").required = true;
				document.getElementById("app_name").required = false;
				document.getElementById("app_id").required = false;
			} else if (store == "appStore") {
				apple.style.display = "block";
				google.style.display = "none";
				document.getElementById("app_name").required = true;
				document.getElementById("app_id").required = true;
				document.getElementById("package_name").required = false;
			}
		}
	}
}

