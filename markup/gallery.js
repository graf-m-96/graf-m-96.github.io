var ID_CURRENT_PHOTO = null;


function changeStartPicture(element) {
    document.getElementById('start_picture').src = element.src;
    var cookie_date = new Date();
    cookie_date.setFullYear(cookie_date.getFullYear() + 2);
    document.cookie = 'start=' + element.id + ";expires=" + cookie_date.toGMTString() + ';path=/';
}


function setStartPictureFromCookies() {
    var seekingString = 'start=';
    var startIndex = document.cookie.indexOf(seekingString) + seekingString.length;
    var lastIndex = document.cookie.indexOf(';') !== -1 ? document.cookie.indexOf(';'):
                                                          document.cookie.length;
    var idFromCookies = document.cookie.substring(startIndex, lastIndex);
    if (idFromCookies.length !== 0) {
        changeStartPicture(document.getElementById(idFromCookies));
    }
}


function keyDown(event) {
    var changedIndex, changedId;
    switch (event.keyCode) {
        // f1
        case 112:
            event.preventDefault();
            closeAllWindows();
            changeVisibilityHelp('block');
            history.pushState(null, '', '?help');
            break;
        // esc
        case 27:
            event.preventDefault();
            closeAllWindows();
            history.pushState(null, '', '?');
            break;
        // влево
        case 37:
            if (document.getElementById(ID_CURRENT_PHOTO) === null) {
                break;
            }
            changedIndex = parseInt(ID_CURRENT_PHOTO.charAt(ID_CURRENT_PHOTO.length - 1)) - 1;
            changedId = ID_CURRENT_PHOTO.substr(0, ID_CURRENT_PHOTO.length - 1) +
                        changedIndex;
            if (document.getElementById(changedId) === null) {
                break;
            }
            closeAllWindows();
            changeVisibilityBigPicture('block', document.getElementById(changedId));
            break;
        // вправо
        case 39:
            if (document.getElementById(ID_CURRENT_PHOTO) === null) {
                break;
            }
            changedIndex = parseInt(ID_CURRENT_PHOTO.charAt(ID_CURRENT_PHOTO.length - 1)) + 1;
            changedId = ID_CURRENT_PHOTO.substr(0, ID_CURRENT_PHOTO.length - 1) +
                        changedIndex;
            if (document.getElementById(changedId) === null) {
                break;
            }
            closeAllWindows();
            changeVisibilityBigPicture('block', document.getElementById(changedId));
            break;
    }
}


function closeAllWindows() {
    changeVisibilityHelp('none', true);
    changeVisibilityBigPicture('none', document.getElementById(ID_CURRENT_PHOTO),  true);
    ID_CURRENT_PHOTO = null;
}


function changeVisibilityHelp(state, keepState) {
    if (!keepState && state === 'none') {
        history.pushState(null, '', '?');
    }
    document.getElementById('help_window').style.display = state;
    document.getElementById('dark_background').style.display = state;
}


function changeVisibilityBigPicture(state, element, keepState) {
    if (!keepState && state === 'none') {
        history.pushState(null, '', '?');
    }
    document.getElementById('dark_background').style.display = state;
    document.getElementById('image_with_cross').style.display = state;
    if (state === 'block') {
        loadImage(element, keepState);
    } else {
        document.getElementById('image_with_cross').style.display = 'none';
    }
}


function loadImage(element, keepState) {
    document.getElementById('big_picture').src = element.src;
    document.getElementById('image_with_cross').style.display = 'block';
    document.getElementById('dark_background').style.display = 'block';
    ID_CURRENT_PHOTO = element.id;
    if (!keepState) {
        history.pushState(null, '', '?' + ID_CURRENT_PHOTO);
    }
    loadingAdjacentImages(element);
}


function loadingAdjacentImages(element) {
    loadPastImages(element);
    loadNextImages(element);
}

function loadPastImages(element) {
    var changedIndex = parseInt(element.id.charAt(element.id.length - 1)) - 1;
    var changedId = element.id.substr(0, element.id.length - 1) + changedIndex;
    var leftElement = document.getElementById(changedId);
    if (leftElement !== null) {
        new Image().src = leftElement.src;
    }
}


function loadNextImages(element) {
    var changedIndex = parseInt(element.id.charAt(element.id.length - 1)) + 1;
    var changedId = element.id.substr(0, element.id.length - 1) + changedIndex;
    var rightElement = document.getElementById(changedId);
    if (rightElement !== null) {
        new Image().src = rightElement.src;
    }
}


function watchForHistory() {
    closeAllWindows();
    var indexQuestion = window.location.href.lastIndexOf('?');
    if (indexQuestion !== -1) {
        var location = window.location.href.substring(indexQuestion + 1,
                                                      window.location.href.length);
        switch (location) {
            case 'help':
                closeAllWindows();
                changeVisibilityHelp('block');
                break;
            case '':
                closeAllWindows();
                break;
            default:
                closeAllWindows();
                if (document.getElementById(location) !== null) {
                    loadImage(document.getElementById(location), true);
                }
                break;
        }
    } else {
        closeAllWindows();
    }
    window.addEventListener('popstate', function(e) {
        var indexQuestion = window.location.href.lastIndexOf('?');
        if (indexQuestion !== -1) {
            var location = window.location.href.substring(indexQuestion + 1,
                                                          window.location.href.length);
            switch (location) {
                case 'help':
                    closeAllWindows();
                    changeVisibilityHelp('block');
                    break;
                case '':
                    closeAllWindows();
                    break;
                default:
                    closeAllWindows();
                    if (document.getElementById(location) !== null) {
                        loadImage(document.getElementById(location), true);
                    }
                    break;
            }
        } else {
            closeAllWindows();
        }
    });
}