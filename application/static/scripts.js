// Color variables referenced from style sheet. Used in front page animation (user index) but must be avaiable to all pages
var colorpurp1 = getComputedStyle(document.documentElement).getPropertyValue('--color-purp1');
var colorpurp2 = getComputedStyle(document.documentElement).getPropertyValue('--color-purp2');
var colorpurp3 = getComputedStyle(document.documentElement).getPropertyValue('--color-purp3');
var colorred1 = getComputedStyle(document.documentElement).getPropertyValue('--color-red1');
var colorred2 = getComputedStyle(document.documentElement).getPropertyValue('--color-red2');
var coloryel1 = getComputedStyle(document.documentElement).getPropertyValue('--color-yel1');
var coloryel2 = getComputedStyle(document.documentElement).getPropertyValue('--color-yel2');
var coloryel3 = getComputedStyle(document.documentElement).getPropertyValue('--color-yel3');


// Enable tooltips across pages
$(function () {
    $('[data-toggle="tooltip"]').tooltip({
        'delay': { show: 500, hide: 500 }
    });

   $('[data-toggle="tooltip"]').on('click', function () {
    $(this).tooltip('hide')
    });
})



// INSERTING SYMBOLS TO STRING FIELD (used across pages for inputting special IPA characters to input fields)
selected_input = "hej";

$(".sound_input_field" ).focus(function() {
    selected_input = this;
    });  
    
function insertAtCursor(sound) {
    if (typeof (selected_input) === "object") {
        $(selected_input).val($(selected_input).val() + sound);
    }
};



// AJAX functions for adding and removing from collection
// keep track of what words and word groups are in the window
var renderedids = [];
var renderedWordGroups = [];

function add_to_collection(id, url_for, event) {
    /** Adds a word of a given id to collection from anywhere  */
    // preventDeafault prevents the <a href="#"> action which takes you to top of page
    event.preventDefault();
    
    $.ajax({
        data: {
            id: id
        },
        // Scripts.js is NOT dynamically generated and therefore dynamic url_for can't be used.
        url: url_for,
        type: "POST"

    }).done(function (data) {
        session = data["session"];
        refreshBtns([id], session);
    });
}

function remove_from_collection(id, url_for, event) {
    /** Removes all rendered words from collection  */
    event.preventDefault();
    $.ajax({
        // sending word ID to "deletion" route
        data: {
            id: id
        },
        // Scripts.js is NOT dynamically generated and therefore dynamic url_for can't be used.
        url: url_for,
        type: "POST"

    }).done(function (data) {
        session = data["session"];
        // removing wordcol only applies in collection page
        $("#wordcol" + id).remove();
        refreshBtns([id], session);
    });
}

function collect_many(ids, url_for, event, remove=false) {
    /** Adds all rendered words to collection from sound search page  */
    // preventDeafault prevents the <a href="#"> action which takes you to top of page

    console.log("clicked collect/remove many");
    console.log("incoming ids " + ids);
    console.log(url_for);
    console.log(remove);

    event.preventDefault();
    jsonids = JSON.stringify(ids)

    console.log(jsonids);
    
    $.ajax({
        data: {
            ids: jsonids,
            remove: remove
        },
        // Scripts.js is NOT dynamically generated and therefore dynamic url_for can't be used.
        url: url_for,
        type: "POST"

    }).done(function (data) {
        session = data["session"];
        refreshBtns(ids, session);
    });
}

function clear_collection(url_for, event) {
    /** Clears collection when garbage icon is clicked (collection page)  */
    // preventDeafault prevents the <a href="#"> action which takes you to top of page
    event.preventDefault();
    
    $.ajax({
        // Scripts.js is NOT dynamically generated and therefore dynamic url_for can't be used.
        url: url_for,
        type: "POST"
    });
    $(".wordcols").remove();
}

// "internal" functions that are only called from scripts.js :
function refreshBtns(wordids, session) {
    /** Refreshes add/remove buttons on single words in both collection and search sounds pages  */
    var i;
    for (i = 0; i < wordids.length; i++) {
        id = wordids[i];
        if (session.includes(id)) {
            $(".w" + id + "-add").hide();
            $(".w" + id + "-remove").show();
        }
        else {
            $(".w" + id + "-add").show();
            $(".w" + id + "-remove").hide();
        }
    }

    // refreshes add/remove buttons for all grouped words (all/pairs/MOs)
    if (typeof renderedids !== typeof undefined) {
        refreshWordGroupBtns(session);
    }
}

function refreshWordGroupBtns(session) {

    /* 
    Checks session for all .wordgroup data-ids (contained words)
    and updates add/remove buttons in these elements.
    */

    $('.wordgroup').each(function(){

        var groupids = $(this).data("ids");
        var allCollected = true;

        for (i = 0; i < groupids.length; i++) {
            if (!session.includes(groupids[i])) {
                allCollected = false;
            }
        }
        if (allCollected) {
            console.log("pair collected: " + groupids);
            $(this).find( ".removegroupbtn" ).show();
            $(this).find( ".addgroupbtn" ).hide();
        }
        else {
            console.log("pair not collected: " + groupids);
            $(this).find( ".removegroupbtn" ).hide();
            $(this).find( ".addgroupbtn" ).show();
        }
    
     });
}


// For admin add for suggesting words to admin when adding

let suggested_indexes = [];

$("#pairs").on("chosen:showing_dropdown", function(e) {
// In dropdown: Highlight suggested words based on "suggested indexes" if any

    var words_in_dropdown = $("#pairs_chosen .active-result");
    words_in_dropdown.each(function( index ) {
        dropdown_index = parseInt($(this).attr("data-option-array-index"));
        // If the dropdown index is one of the suggested, set CSS class "suggested-result"
        if (suggested_indexes.includes(dropdown_index)) {
            $(this).addClass("suggested-result");
        }
    });
});

function display_suggested_words(indexes) {
    var words_in_multiselect = $("#pairs option");
    var display_container = $("#word-suggestions");
    display_container.empty();
    words_in_multiselect.each(function( index ) {
        // dropdown_index = parseInt($(this).attr("data-option-array-index"));
        // If the dropdown index is one of the suggested, set CSS class "suggested-result"
        if (indexes.includes(index)) {
            var display_element = $("<div></div>", {"class": "word-suggestion"});
            var display_text =  $(this).html();
            display_element.text(display_text);
            display_container.append(display_element);
        }

    });
}


$('#pairs').on('change', function(evt, params) {
    console.log(params);
    console.log(params.selected);
// Ajax call to get suggested words based on selected ones and highlight them

    var selected_partner_ids = [];
    var selected_partner_elements = $("#pairs_chosen .search-choice a");
    var all_partners_elements = $("#pairs option");
    var all_ids_indexed = []
    
    all_partners_elements.each(function( index ) {
        // Make array to see what indexes belong with which word ids
        id = $(this).val();
        all_ids_indexed.push(parseInt(id));
    });

    selected_partner_elements.each(function( index ) {
        // See what indexes have been selected
        array_index = $(this).attr("data-option-array-index");
        selected_id = get_id_from_index(all_ids_indexed, this);
        if (parseInt(params.deselected) !== selected_id) {
            selected_partner_ids.push(selected_id)
        }
    });

    $.ajax({
        data: {
            chosen_ids : JSON.stringify(selected_partner_ids),
            all_indexes : JSON.stringify(all_ids_indexed)
        },
        url: url_for_suggested_pairs,
        type: "POST"

    }).done(function (data) {
        /* Suggested indexes is keeping track of which words in the dropdown to highlight */
        console.log("DATA:")
        if (typeof data["suggested_indexes"] !== "undefined") {
            suggested_indexes = data["suggested_indexes"];
            suggested_ids = data["suggested_ids"];
            // If I regret auto-adding: remove "update_chosen_selection" and 
            // reenable display_suggested_words(...) which relies on suggested_idexes
            //display_suggested_words(suggested_indexes);

            update_chosen_selection(suggested_ids)
        }
        else {
            console.log("error retriving suggestions")
        }
    });
});

function get_id_from_index(all_ids_indexed, selected_partner_elem) {
    array_index = $(selected_partner_elem).attr("data-option-array-index");
    var selected_id = all_ids_indexed[parseInt(array_index)];
    return parseInt(selected_id);
}

function update_chosen_selection(suggested_ids) {

    existing_selection = $('#pairs').val();
    existing_selection_ints = []
    $.each(existing_selection, function(index) {
        existing_selection_ints.push(parseInt(this));
    });
    updated_selection = $.merge(existing_selection_ints, suggested_ids)
    console.log($('#pairs').val());
    console.log(updated_selection);
    $('#pairs').val(updated_selection);
    $('#pairs').trigger('chosen:updated');
}