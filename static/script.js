// getting all required elements
const searchWrapper = document.querySelector(".search-input");
const inputBox = searchWrapper.querySelector("input");
const suggBox = searchWrapper.querySelector(".autocom-box");
const icon = searchWrapper.querySelector(".icon");
let linkTag = searchWrapper.querySelector("a");
let webLink;
let emptyArray = [];

// if user press any key and release
inputBox.onkeyup = (e) => {
    let userData = e.target.value;
    if (userData) {
        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/search_char', true);
        xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhr.onreadystatechange = function () {
            if (xhr.readyState === 4) {
                if (xhr.status === 200) {
                    var responseData = JSON.parse(xhr.responseText);
                    emptyArray = responseData;
                    emptyArray = emptyArray.map((data) => {
                        return data = `<li>${data}</li>`;
                    });
                    searchWrapper.classList.add("active"); //show autocomplete box
                    showSuggestions(emptyArray);
                    let allList = suggBox.querySelectorAll("li");
                    for (let i = 0; i < allList.length; i++) {
                        //adding onclick attribute in all li tag
                        allList[i].setAttribute("onclick", "select(this)");
                    }
                    emptyArray.length = 0;
                } else {
                    console.log(xhr.statusText);
                }
            }
        };
        xhr.onerror = function (error) {
            console.log(error);
        };
        xhr.send('q=' + encodeURIComponent(userData));
        icon.onclick = () => {
            webLink = `https://www.google.com/search?q=${userData}`;
            linkTag.setAttribute("href", webLink);
            linkTag.click();
        }
    } else {
        searchWrapper.classList.remove("active"); //hide autocomplete box
    }
}

suggBox.addEventListener("click", (e) => {
    const searchTerm = inputBox.value;
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/update_freq', true);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
            } else {
                console.log(xhr.statusText);
            }
        }
    };
    xhr.onerror = function (error) {
        console.log(error);
    };
    xhr.send('q=' + encodeURIComponent(searchTerm));
})

function convert(str) {
    return decodeURIComponent(JSON.parse('"' + str.replace(/\"/g, '\\"') + '"'));
}

function select(element) {
    let selectData = element.textContent;
    inputBox.value = selectData;
    icon.onclick = () => {
        webLink = `https://www.google.com/search?q=${selectData}`;
        linkTag.setAttribute("href", webLink);
        linkTag.click();
        alert("clicked");
    }
    searchWrapper.classList.remove("active");
}

function showSuggestions(list) {
    let listData;
    if (!list.length) {
        userValue = inputBox.value;
        listData = `<li>${userValue}</li>`;
    } else {
        listData = list.join('');
    }
    suggBox.innerHTML = listData;
}
