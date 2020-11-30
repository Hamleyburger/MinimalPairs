// HAVING TO DO WITH FILE INPUT FIELDS
// Makes file names of chosen files show in file input fields given the right label
$(document).ready(function () {
    $('input[type="file"]').change(function (e) {
        var fileName = e.target.files[0].name;
        $('.file-label-name').html(fileName);
        //alert('The file "' + fileName + '" has been selected.');
    });
});


// HAVING TO DO WITH CHOSEN.JS SELECT FIELDS
// Gives select fields with class chosen-select jQuery chosen.js functionality
$(document).ready(function () {
    $(".chosen-select").chosen({ search_contains: true });
    $("#word1").change()

});
// If js is deactivated chosen-select options are populated by all choices
// if js is active use ajax to filter out words that are already paired.

// .chosen-word .pairs-select
$("#word1").change(function () {
    console.log("Changed");

    console.log("ajax call from js");
    $.ajax({
        data: {
            id: $("#word1").val(),
        },
        // ajax is the name of the view function that processes the incoming ajax call
        url: "/ajax_possible_pairs",
        type: "POST"

    }).done(function (data) {
        /* Server check: with parents().length I check if element has any parent with this ID
        because an existing username is good (green) in Login but bad (red) in register. */

        $("#pairs > option").each(function() {
            if (data.id.includes(parseInt(this.value))) {
                this.disabled = true;
            }
            else {
                this.disabled = false;
            }
        });
        $("#pairs").trigger("chosen:updated");


        //$("#word" + current_word_id).html(data.newword);
        //$("#cue" + current_word_id).html(data.newcue);
        //$("#image" + current_word_id).html(data.newimg);
    });
});


// INSERTING SYMBOLS TO STRING FIELD

selected_input = "hej";


$(".sound_input_field" ).focus(function() {
    selected_input = this;
    });  
    
function insertAtCursor(sound) {
    if (typeof (selected_input) === "object") {
        console.log(selected_input);
        $(selected_input).val($(selected_input).val() + sound);
    }
};


// Having to do with js controlled style and the (front page) animation
var colorpurp1 = getComputedStyle(document.documentElement).getPropertyValue('--color-purp1');
var colorpurp2 = getComputedStyle(document.documentElement).getPropertyValue('--color-purp2');
var colorpurp3 = getComputedStyle(document.documentElement).getPropertyValue('--color-purp3');
var colorred1 = getComputedStyle(document.documentElement).getPropertyValue('--color-red1');
var colorred2 = getComputedStyle(document.documentElement).getPropertyValue('--color-red2');
var coloryel1 = getComputedStyle(document.documentElement).getPropertyValue('--color-yel1');
var coloryel2 = getComputedStyle(document.documentElement).getPropertyValue('--color-yel2');

var tl = gsap.timeline({
    scrollTrigger: {
        once: true,
        end: "+=500", // end after scrolling 500px beyond the start
        scrub: 2, // smooth scrubbing, takes 1 second to "catch up" to the scrollbar
    }
});
tl.delay(1);
tl.timeScale(0.5);
// solen tager 5s om at gå ned
tl.to("#sun", { duration: 5, y: 190 })
    // lyset tager 8s om at gå ned
    .to("#sun-gradient", { duration: 7, attr: { fy: 0.9 } }, '<')
    // lyset tager 3s om at blive rødt
    .to("#outer-c", { duration: 3, stopColor: colorred1 }, '<')
    .to("#inner-c", { duration: 1, stopColor: colorred1 }, '>')
    .to("#sun", { duration: 0, autoAlpha: 0 }, '>')
    //.to("#inner-c", { duration: 2, stopColor: colorred1 }, '>')
    .to("#outer-c", { duration: 1, stopColor: colorpurp2 }, '<')




// Functions for adding to and removing words from session with AJAX
// Used in "contrasts" and "collection"
function add_to_collection(id, event) {
    // preventDeafault prevents the <a href="#"> action which takes you to top of page
    event.preventDefault();
    console.log("ajax call to add word to collection");
    $.ajax({
        // sending word ID to "deletion" route
        data: {
            id: id
        },
        // url is the ajax route in views.py
        url: "/ajax_add2collection",
        type: "POST"

    }).done(function (data) {
        console.log("data is: " + data);
        $(".w" + id + "show").toggle();
    });
}

function remove_from_collection(id, event) {
    event.preventDefault();
    console.log("ajax call to add word to collection");
    $.ajax({
        // sending word ID to "deletion" route
        data: {
            id: id
        },
        // url is the ajax route in views.py
        url: "/ajax_remove_from_collection",
        type: "POST"

    }).done(function (data) {
        console.log("data is: " + data);
        $("#wordcol" + id).remove();
        console.log(event.target.parentNode);
        $(".w" + id + "show").toggle();
    });
}