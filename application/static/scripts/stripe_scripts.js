console.log("loaded stripe scripts");

// Get Stripe publishable key
fetch("/ajax_get_stripe_key")
.then((result) => { return result.json(); })
.then((data) => {
  // Initialize Stripe.js
  const stripe = Stripe(data.publicKey);


  // Event handler
  $(".stripe-submitBtn").click(function(){

    product_id = $(this).data("id");
    const requestOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ product_id: product_id })
    };
    // Get Checkout Session ID
    fetch("/ajax-create-checkout-session", requestOptions)
    .then((result) => { return result.json(); })
    .then((data) => {
      console.log(data);
      // Redirect to Stripe Checkout
      return stripe.redirectToCheckout({sessionId: data.sessionId})
    })
    .then((res) => {
      console.log(res);
    });
  });





});

// https://testdriven.io/blog/flask-stripe-tutorial/