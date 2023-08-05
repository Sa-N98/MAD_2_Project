
    //trigger slide animation//
    let box = document.querySelector('#login');
    let button = document.querySelector('button');
    let flag = 0
    button.addEventListener('click', function () {

      if (button.innerHTML === 'SIGNUP') {
        button.innerHTML = "LOGIN"
      } else {
        button.innerHTML = "SIGNUP";
      }


      if (flag === 0) {
        box.classList.toggle('move-left')
        flag = 1;
        console.log('left')
        return null
      }

      if (flag === 1) {
        box.classList.toggle('move-right');
        flag = 1;
        console.log('right')
        return null
      }

    });




    // submition of signup form
    let signupForm = document.getElementById('signupForm')

    signupForm.addEventListener("submit", function (event) {
      event.preventDefault(); // Prevent form from submitting normally

      // Get form data
      var formData = new FormData(signupForm);

      // Send form data to Flask route
      fetch("/submit", {
          method: "POST",
          body: formData
        })
        .then(function (response) {
          // Handle response from the Flask route
          if (response.ok) {
            console.log('Successful submmition')
            // Do something with the response data
          } else {
            // Error occurred
            // Handle the error
          }
        })
        .catch(function (error) {
          // Handle network or other errors
        });
    });


    //trigers click on button to invoke animation//
    let signupButton = document.getElementById("signupButton")


    signupButton.addEventListener('click', function () {

      fetch('/click').then(function (response) {
          return response.text();
        })
        .then(function (message) {
          if (message === 'true') {
            if (signupForm.checkValidity() === true) {
              button.click();
            }
          }; // Display the response message
        })
        .catch(function (error) {
          console.error('Error:', error);
        });

    })