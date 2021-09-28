const audiobookContainer = document.querySelector('.audiobook-container')
const playBtn = document.querySelector('#play')
const prevBtn = document.querySelector('#prev')
const nextBtn = document.querySelector('#next')
const audio = document.querySelector('#audio')
const progress = document.querySelector('.progress')
const progressContainer = document.querySelector('.progress-container')
const title = document.querySelector('#title')
const cover = document.querySelector('#cover')
 
// audiobook titles
const audiobooks = ['Game of Throne', 'Harry Potter' , 'Demon Slayer']

// keep track of audiobooks
let audiobookIndex = 2

// initially load song info DOM
loadAudiobook(audiobooks[audiobookIndex])


function myFunc(vars) {
    return vars
}

function test_func(data) {
    // JSON.parse( decodeURIComponent( data) );
    // console.log(data);
    return data
}


// update song details
function loadAudiobook(audiobook) {
    title.innerText = audiobook
    audio.src = `../static/audios/${audiobook}.wav`
    cover.src = `../static/images/cover/${audiobook}.jpg`
}

function playAudiobook() {
    audiobookContainer.classList.add('play')
    playBtn.querySelector('i.fas').classList.remove('fa-play')
    playBtn.querySelector('i.fas').classList.add('fa-pause')

    audio.play()
}

function pauseAudiobook() {
    audiobookContainer.classList.remove('play')
    playBtn.querySelector('i.fas').classList.remove('fa-pause')
    playBtn.querySelector('i.fas').classList.add('fa-play')

    audio.pause()
}

function prevAudiobook() {
    audiobookIndex--

    if(audiobookIndex < 0) {
        audiobookIndex = audiobooks.length - 1
    }

    loadAudiobook(audiobooks[audiobookIndex])

    playAudiobook()
}

function nextAudiobook() {
    audiobookIndex++

    if(audiobookIndex > audiobooks.length - 1) {
        audiobookIndex = 0
    }

    loadAudiobook(audiobooks[audiobookIndex])

    playAudiobook()
}

function updateProgress(e) {
    // console.log(e.srcElement.currentTime)
    // console.log(e.srcElement.duration)
    const {duration, currentTime} = e.srcElement
    const progressPercent = (currentTime / duration) * 100
    progress.style.width = `${progressPercent}%`
}

// set progress bar
function setProgress(e) {
    const width = this.clientWidth;
    const clickX = e.offsetX;
    const duration = audio.duration;
  
    audio.currentTime = (clickX / width) * duration;
  }

// event listeners
playBtn.addEventListener('click', () => {
    const isPlaying = audiobookContainer.classList.contains('play')

    if(isPlaying) {
        pauseAudiobook()
    } else {
        playAudiobook()
    }
})

// change audiobook events
prevBtn.addEventListener('click', prevAudiobook)
nextBtn.addEventListener('click', nextAudiobook)

audio.addEventListener('timeupdate', updateProgress);

progressContainer.addEventListener('click', setProgress);