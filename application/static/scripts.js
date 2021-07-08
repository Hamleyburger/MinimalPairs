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


// AJAX and JS funcitons for for adding custom images temporarily to collection,
// cropping them and uploading the cropped version all while keeping track of the
// word id.

let upload_word_id;

function set_upload_word_id(id) {
    console.log("Setting word id to " + id);
    $("#upload_word_id").attr("value",id);
    upload_word_id = id;
}

function uploadFile() {


    var form_data = new FormData($('#upload-file')[0]);
    var files = $('#image')[0].files;
    
    // Check file selected or not
    if(files.length > 0 ){
        
        $.ajax({
            type: 'POST',
            url: upload_url,
            data: form_data,
            contentType: false,
            cache: false,
            processData: false,
            success: function(data) {
                console.log('Success!');
            },
        }).done(function(data) {
            if (data.error) {
                
                alert(data.error)
            }
            else {
                    $("#croppermodal").modal("show");
                    unique = Date.now();
                    $('#croppermodal').on('shown.bs.modal', function () {
                        // your on click event binding here.
                
                        // example of triggering an input.
                        $("#cropperimage").attr("src", data.path + "?" + unique );
                        start_cropper(data.path);
                        console.log("WORD ID LET = " + upload_word_id);

                    })
                }
           });
        }else{
           alert("Please select a file.");
        }

}



function start_cropper(new_url) {
    const image = document.getElementById('cropperimage');

    console.log("starting cropper");

    
    const cropper = new Cropper(image, {
        aspectRatio: 16 / 9,
        crop(event) {
            // console.log(event.detail.x);
            // console.log(event.detail.y);
            // console.log(event.detail.width);
            // console.log(event.detail.height);
            // console.log(event.detail.rotate);
            // console.log(event.detail.scaleX);
            // console.log(event.detail.scaleY);
        },
    });

    // make sure image gets refreshed when start_cropper is called
    image.cropper.replace(new_url);


}


// End of collection-related AJAX

