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


// AJAX functions for adding and removing from collection
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
    event.preventDefault();
    jsonids = JSON.stringify(ids)
    
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

    // pairwordids and renderedids are only defined in the template for search sounds
    if (typeof pairwordids !== typeof undefined && typeof renderedids !== typeof undefined) {
        refreshAddAllBtns(session);
        refreshPairBtns(session);
    }
}

// used in refreshBtns if required variable exists
function refreshAddAllBtns(session) {
    /** Changes the add/remove "all" buttons (in sound search page) if all words are/are not in collection\n
     * Requires the global variable: renderedids to have been declared.
      */
    var i;
    allAdded = true;
    allRemoved = true;

    for (i = 0; i < renderedids.length; i++) {
        id = renderedids[i];
        if (!session.includes(id)) {
            allAdded = false;
        }
        else {
            allRemoved = false;
        }
    }
    if (allAdded) {
        $(".removeallbtn").show();
        $(".addallbtn").hide();
    }
    else if (allRemoved) {
        $(".removeallbtn").hide();
        $(".addallbtn").show();
    }
}

// used in refreshBtns if required variable exists
function refreshPairBtns(session) {
    /** Checks a list of two pair ids and refreshes its add/remove button  */

    var i;
    for (i = 0; i < pairwordids.length; i++) {
      pair = pairwordids[i];
      if (session.includes(pair[0]) && session.includes(pair[1])) {
          id_string_add="#pair-" + pair[0] + "vs" + pair[1] + "-addbtn";
          id_string_remove="#pair-" + pair[0] + "vs" + pair[1] + "-removebtn";
          $(id_string_add).hide();
          $(id_string_remove).show();
      }
      else if (!session.includes(pair[0]) && !session.includes(pair[1])) {
          id_string_add="#pair-" + pair[0] + "vs" + pair[1] + "-addbtn";
          id_string_remove="#pair-" + pair[0] + "vs" + pair[1] + "-removebtn";
          $(id_string_add).show();
          $(id_string_remove).hide();
      }

    }

}

