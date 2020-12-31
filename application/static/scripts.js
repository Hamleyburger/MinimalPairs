// Enable tooltips across pages
$(function () {
    $('[data-toggle="tooltip"]').tooltip({
        'delay': { show: 1000, hide: 500 }
   });
})



// INSERTING SYMBOLS TO STRING FIELD (used across pages for inputting special IPA characters to input fields)
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




// Color variables referenced from style sheet. Used in front page animation (user index) but must be avaiable to all pages
var colorpurp1 = getComputedStyle(document.documentElement).getPropertyValue('--color-purp1');
var colorpurp2 = getComputedStyle(document.documentElement).getPropertyValue('--color-purp2');
var colorpurp3 = getComputedStyle(document.documentElement).getPropertyValue('--color-purp3');
var colorred1 = getComputedStyle(document.documentElement).getPropertyValue('--color-red1');
var colorred2 = getComputedStyle(document.documentElement).getPropertyValue('--color-red2');
var coloryel1 = getComputedStyle(document.documentElement).getPropertyValue('--color-yel1');
var coloryel2 = getComputedStyle(document.documentElement).getPropertyValue('--color-yel2');


// Functions for adding to and removing words from session with AJAX
// Used in "contrasts" - "collection" - "wordinfo"
function add_to_collection(id, url_for, event) {
    // preventDeafault prevents the <a href="#"> action which takes you to top of page
    event.preventDefault();
    console.log("ajax call to add word to collection");
    
    $.ajax({
        data: {
            id: id
        },
        // Scripts.js is NOT dynamically generated and therefore dynamic url_for can't be used.
        url: url_for,
        type: "POST"

    }).done(function (data) {
        console.log("data is: " + data);
        $(".w" + id + "show").toggle();
    });
}

function remove_from_collection(id, url_for, event) {
    event.preventDefault();
    console.log("ajax call to add word to collection");
    $.ajax({
        // sending word ID to "deletion" route
        data: {
            id: id
        },
        // Scripts.js is NOT dynamically generated and therefore dynamic url_for can't be used.
        url: url_for,
        type: "POST"

    }).done(function (data) {
        console.log("data is: " + data);
        $("#wordcol" + id).remove();
        console.log(event.target.parentNode);
        $(".w" + id + "show").toggle();
    });
}

function add_pair_to_collection(ids, url_for, event) {
    // preventDeafault prevents the <a href="#"> action which takes you to top of page
    event.preventDefault();
    console.log("ajax call to add PAIR to collection");
    
    $.ajax({
        data: {
            ids: ids
        },
        // Scripts.js is NOT dynamically generated and therefore dynamic url_for can't be used.
        url: url_for,
        type: "POST"

    }).done(function (data) {
        console.log("data is: " + data);
        $(".w" + id + "show").toggle();
    });
}
