const lightMode = 'default_scheme';
const darkMode = 'dark_scheme';
const darkSchemeMedia = matchMedia('(prefers-color-scheme: dark)');
const switcherRadios = document.querySelectorAll('.theme-switcher__radio');


function setupSwitcher() {
    const savedScheme = getSavedScheme();

    if (savedScheme === 'light' || savedScheme === 'dark') {
        const currentRadio = document.querySelector(`.theme-switcher__radio[value=${savedScheme}]`);
        currentRadio.checked = true;
        switchMedia(savedScheme);
    }

    [...switcherRadios].forEach((radio) => {
        radio.addEventListener('change', (event) => {
            setScheme(event.target.value);
        });
    });
}


function setupScheme() {
    const savedScheme = getSavedScheme();
    const systemScheme = getSystemScheme();

    if (savedScheme === null) {
        setScheme('auto');
    }

    if (savedScheme !== systemScheme) {
        setScheme(savedScheme);
    }
}

function setScheme(scheme) {
    switchMedia(scheme);

    if (scheme === 'auto') {
        clearScheme();
    } else {
        saveScheme(scheme);
    }
}

function switchMedia(scheme) {
    const body = document.querySelector('body');

    if (scheme === 'auto') {
        if (getSystemScheme() === 'dark') {
            body.classList.remove(lightMode);
            body.classList.add(darkMode);
        } else {
            body.classList.remove(darkMode);
            body.classList.add(lightMode);
        }
    } else if (scheme === 'light') {
        body.classList.remove(darkMode);
        body.classList.add(lightMode);
    } else if (scheme === 'dark') {
        body.classList.remove(lightMode);
        body.classList.add(darkMode);
    }
}

function getSystemScheme() {
    const darkScheme = darkSchemeMedia.matches;

    return darkScheme ? 'dark' : 'light';
}

function getSavedScheme() {
    return localStorage.getItem('color-scheme');
}

function saveScheme(scheme) {
    localStorage.setItem('color-scheme', scheme);
}

function clearScheme() {
    localStorage.removeItem('color-scheme');
}

setupSwitcher();
setupScheme();


// ToTop
const toTopBtn = document.querySelector('.scrollTop');
const scrollSection = document.querySelector('main');

scrollSection.addEventListener('scroll', scrollFunction);
toTopBtn.addEventListener('click', topFunction);

function scrollFunction() {
    console.log(scrollSection.scrollTop)
    if (scrollSection.scrollTop > 100 || scrollSection.scrollTop >100) {
        toTopBtn.classList.add('showBtn');
    } else {
        toTopBtn.classList.remove('showBtn');
    }
}

function topFunction() {
    scrollSection.scrollTop = 0;
    scrollSection.scrollTop = 0;
}