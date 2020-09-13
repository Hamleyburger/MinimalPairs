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


