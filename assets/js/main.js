
AOS.init({
  // Settings that can be overridden on per-element basis, by `data-aos-*` attributes:
//   offset: 120, // offset (in px) from the original trigger point
//   delay: 0, // values from 0 to 3000, with step 50ms
//   duration: 900, // values from 0 to 3000, with step 50ms
//   easing: 'ease', // default easing for AOS animations
//  once: false, // whether animation should happen only once - while scrolling down
//   mirror: false, // whether elements should animate out while scrolling past them
//   anchorPlacement: 'top-bottom', // defines which position of the element regarding to window should trigger the animation

});


      // document.getElementById("form").addEventListener("submit", function (e) {
      //   e.preventDefault(); // Prevent the default form submission
      //   document.getElementById("message").textContent = "Submitting..";
      //   document.getElementById("message").style.display = "block";
      //   document.getElementById("submit-button").disabled = true;

      //   // Collect the form data
      //   var formData = new FormData(this);
      //   var keyValuePairs = [];
      //   for (var pair of formData.entries()) {
      //     keyValuePairs.push(pair[0] + "=" + pair[1]);
      //   }

      //   var formDataString = keyValuePairs.join("&");

      //   // Send a POST request to your Google Apps Script
      //   fetch(
      //     "https://script.google.com/macros/s/AKfycbw_pWlZ7RwfTuy4cP_j4WRX3RcgowWkxUe1kKGIXiIg2MYZe1zVhpDxw-vpcmNHYbCu6Q/exec",
      //     {
      //       redirect: "follow",
      //       method: "POST",
      //       body: formDataString,
      //       headers: {
      //         "Content-Type": "text/plain;charset=utf-8",
      //       },
      //     }
      //   )
      //     .then(function (response) {
      //       // Check if the request was successful
      //       if (response) {
      //         return response; // Assuming your script returns JSON response
      //       } else {
      //         throw new Error("Failed to save the email.,");
      //       }
      //     })
      //     .then(function (data) {
      //       // Display a success message
      //       document.getElementById("message").textContent =
      //         "Added to the priority waitlist!";
      //       document.getElementById("message").style.display = "block";
      //       document.getElementById("message").style.backgroundColor = "green";
      //       document.getElementById("message").style.color = "beige";
      //       document.getElementById("submit-button").disabled = false;
      //       document.getElementById("form").reset();

      //       setTimeout(function () {
      //         document.getElementById("message").textContent = "";
      //         document.getElementById("message").style.display = "none";
      //       }, 2600);
      //     })
      //     .catch(function (error) {
      //       // Handle errors, you can display an error message here
      //       console.error(error);
      //       document.getElementById("message").textContent =
      //         "An error occurred...";
      //       document.getElementById("message").style.display = "block";
      //     });
      // });
   
    
      var acc = document.getElementsByClassName("planfaq");
      var i;

      for (i = 0; i < acc.length; i++) {
        acc[i].addEventListener("click", function () {
          this.classList.toggle("active");
          this.parentElement.classList.toggle("active");

          var pannel = this.nextElementSibling;

          if (pannel.style.display === "block") {
            pannel.style.display = "none";
          } else {
            pannel.style.display = "block";
          }
        });
      }
  