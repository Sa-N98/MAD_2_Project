
const app = Vue.createApp({
    data() {
        return {
            currentURL: null,
            title: null,
            poster: null,
            banner: null,
            venues: null,
        }
    },
    mounted() {
        this.currentURL = window.location.href.split('/')[4];
        console.log(this.currentURL)

        url = '/api/show-booking-data/' + this.currentURL
        axios.get(url)
            .then(response => {
                this.title = response.data.name
                this.poster = response.data.poster
                this.banner = response.data.posterLong
                this.venues = response.data.venues
            })
            .catch(error => {
                console.error(error);
            });

        let titleHeight = document.getElementById('title')
        let checkHeigth = () => {
            const currentHeight = titleHeight.offsetHeight
            if (currentHeight > 106) {
                titleHeight.style.transform = 'translate(150px, -429px)';
            } else {
                titleHeight.style.transform = 'translate(150px, -359px)';
            }
        }
        setInterval(checkHeigth, 100)
    }
});
app.component('venue', {

    template: `
    <div  class=ticket>
        <div class='venue'>
            <div class='name'>   
                <h3>{{ venue[0][1] }}</h3> 
                <div class='date'>{{ venue[1][1] }} <h4 id='price'>Rs {{ venue[3] }}</h4></div>
                <h4>{{ venue[0][2] }}</h4>
                
            </div>
            <div id='mask' class="noBooking" ><h1>NO BOOKING</h1></div>
            <div class='seats'><h1 id='maxSeatNo'>{{venue[2]}}</h1> <h2>SEATS</h2> </div>
        </div>
        <div class='tkt-counter'>
            <div id="count" >0</div>
            <div class="buttons">
                <div class="square-button plus"></div>
                <div class="square-button minus"></div>
            </div>
            <button @click='book_show' >Book</button>
        </div>
    </div>
    `,
    props: ['venue'],
    data() {
        return {
            availabelSeats: "",
            count: 0
        }
    },
    mounted() {
        console.log(this.venue[4])
        let fontHeightCheck = () => {
            let placeElements = document.querySelectorAll('.name h4')
            placeElements.forEach(h1 => {
                if (h1.offsetHeight > 38) {
                    h1.style.fontSize = '12.5px'
                }
            });

        }

        setInterval(fontHeightCheck, 100)

        const plusButton = this.$el.querySelector('.plus');
        const minusButton = this.$el.querySelector('.minus');
        const countElement = this.$el.querySelector('#count');
        let maxLimit = this.$el.querySelector('#maxSeatNo');
        this.availabelSeats = Number(maxLimit.innerHTML)
        plusButton.addEventListener('click', () => {
            if (maxLimit.innerHTML > 0) {
                this.count++;
                countElement.textContent = this.count;
                maxLimit.innerHTML = maxLimit.innerHTML - 1;
                this.availabelSeats = Number(maxLimit.innerHTML)
            }
        });

        minusButton.addEventListener('click', () => {
            if (this.count > 0) {
                this.count--;
                countElement.textContent = this.count;
                maxLimit.innerHTML = Number(maxLimit.innerHTML) + 1;
                this.availabelSeats = Number(maxLimit.innerHTML)
            }
        });

        // setInterval(()=>{console.log(this.availabelSeats)},1000)
        setInterval(() => {
            this.showNoBooking()
        }, 100)

    },

    methods: {
        showNoBooking: function () {
            if (Number(this.$el.querySelector('#maxSeatNo').innerHTML) === 0 && Number(this.$el
                    .querySelector('#count').innerHTML) === 0) {
                console.log("hi")
                this.$el.querySelector('#mask').style.opacity = 1;
                this.$el.querySelector('#mask h1').style.display = 'block';
                this.$el.querySelector('button').disabled = true;
                this.$el.querySelector('button').style.background = '#c52e31';
            } else {
                this.$el.querySelector('#mask').style.opacity = 0;
                this.$el.querySelector('#mask h1').style.displ = 'none';
                this.$el.querySelector('button').disabled = false;

            }

        },

        book_show: function () {
            // console.log('NO_tickets: ',this.$el.querySelector('#count').innerHTML)
            // console.log('venueID: ',this.venue[0][0])
            // console.log('dateID: ',this.venue[1][0])
            // console.log('movieID: ',this.venue[4])
            // console.log('USER: ','[[ current_user.username ]]')



            if (Number(this.$el.querySelector('#count').innerHTML) > 0) {

                const body = {
                    'USER': '[[ current_user.username ]]',
                    'movieID': this.venue[4],
                    'venueID': this.venue[0][0],
                    'dateID': this.venue[1][0],
                    'NO_tickets': this.$el.querySelector('#count').innerHTML
                }
                const token = localStorage.getItem('access_token');
                let header={headers: {'Authorization': `Bearer ${token}`}}
                axios.post('/api/show_booking', body, header)
                    .then(response => {
                        console.log('Post created:', response.data);
                    })
                    .catch(error => {
                        console.error('Error creating post:', error);
                    });

                axios.put('/api/show_booking', body, header)
                    .then(response => {
                        console.log('Put updated:', response.data);
                    })
                    .catch(error => {
                        console.error('Error creating post:', error);
                    });

                this.$el.querySelector('#count').innerHTML = 0
                this.count = 0
            }


        }
    }
})
app.mount('#app');
