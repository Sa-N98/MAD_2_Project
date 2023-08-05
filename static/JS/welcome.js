
const app = Vue.createApp({
    data(){
        return{
            genres:'',
            venues:'',
            movies:'',
        }
    },
    mounted(){
        axios.get('/api/welcome')
            .then(response => {
                    this.genres=response.data.genres
                    this.venues=response.data.venues_name
                    this.movies=response.data.movie_name
                    
                })
                .catch(error => {
                    console.error(error);
                });
    }
});

app.component('img-carousel', {
template: `
<div class='carousel'>
    <h1 id='title'>{{movies[index]}} </h1>
    <img :src='poster[index]' id='canvas' class='animation'>
</div>
`,
data() {
    return {
        movies: [],
        poster: [],
        index: 0,
        canvas: null,
        titleElement: null
    };
},

mounted() {
    axios.get('/api/movies')
        .then(response => {
            this.movies = response.data.map(show => show.name);
            this.poster = response.data.map(show => show.posterLong);
        })
        .catch(error => {
            console.error(error);
        });
    this.canvas = document.getElementById('canvas');
    this.titleElement = document.getElementById('title');
    setInterval(this.changePoster, 15000);
    this.adjustFontSize()
},

methods: {
    changePoster: function () {
        this.canvas.classList.remove('animation');
        this.index = (this.index + 1) % this.movies.length;
        setTimeout(() => {
            this.canvas.classList.add('animation');
        }, 10);
    },
    adjustFontSize: function () {
        const titleLength = this.titleElement.textContent.length;
        const fontSize = 10 - Number(titleLength);
        this.titleElement.style.fontSize = fontSize + 'vw';
    }
}
});


app.component('movie-cards', {
    template: `
    <div class='card'>
    <div class=content>
        <div class= card-poster>
            <div class='rating'>{{ rating }}/5</div>
            <img :src='poster'>
        </div>
        <div class='info'>
            <h1> {{ title }}</h1>
            <div class='summary'>
                <p>{{ summary }}.</p>
            </div>
        <button  @click="openLink" type="button">Booke A Ticket </button>
        </div>
    </div>
    </div>
    `,

    props: ['title'],
    data() {
        return {
            cards: null,
            poster: sessionStorage.getItem(this.title +' poster'),
            rating: sessionStorage.getItem(this.title +' rating'),
            summary: sessionStorage.getItem(this.title +' summary'),
            show_id: '/booking/'
        }
    },

    mounted() {

        url = '/api/movie/' + this.title
        axios.get(url)
            .then(response => {
                this.rating = response.data.rating
                sessionStorage.setItem(this.title+' rating', this.rating)
                this.poster = response.data.poster
                sessionStorage.setItem(this.title+' poster', this.poster)
                let id = response.data.id
                this.show_id = this.show_id + id
            })
            .catch(error => {
                console.error(error);
            });

        url = 'http://www.omdbapi.com/?t=' + this.title + '&apikey=78f7079e';
        axios.get(url)
            .then(response => {
                this.summary = response.data.Plot
                sessionStorage.setItem(this.title+' summary', this.summary)
            }).catch(error => {
                console.error(error);
            });
    },

    methods: {
        openLink() {
            // window.open(this.show_id);//
            window.location.href = this.show_id
        }
    }
})
app.mount('#app');

function validateForm() {
    let genre = document.getElementById("genre").value;
    let place = document.getElementById("place").value;
    let rating = document.getElementById("rating").value;
    let popup = document.getElementById("pop-massage")
    let popdown = document.getElementById("greatings")
    console.log(genre, place, rating)
    if (genre === "none" && place === "none" && rating === "none") {
        event.preventDefault();
        popup.classList.add("popup");
        popdown.classList.add("popdown");
    }
}
setTimeout(() => {
        const cards = document.getElementsByClassName('card');
                    for (let i = 0; i < cards.length; i++) {
                        const card = cards[i];
                        card.addEventListener('click', function () {
                            // Remove the 'expand' class from all cards
                            for (let j = 0; j < cards.length; j++) {
                                if (cards[j] !== card) {
                                    cards[j].classList.remove('expand');
                                }
                            }

                            // Toggle the 'expand' class on the clicked card
                            card.classList.toggle('expand');
                        });
                    }
}, 500);
