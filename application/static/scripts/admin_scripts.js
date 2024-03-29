
$( document ).ready(function() {

    /*
    line 9-38:
    When admin types in an s1 field that has a suggested partner (based on group),
    this typed sound is transferred to all s1 fields for partners of same group.
    */
    var pairSoundTables = document.querySelectorAll('.pairSoundTable');
    pairSoundTables.forEach(function callback(thing, index) {
        //                              Vigtigt at skelne mellem sound2 og word2_id, id er hidden
        s1inputfield = document.getElementById("pairSounds-" + index + "-sound1");
        s2inputfield = document.getElementById("pairSounds-" + index + "-sound2");
        w2idfield = document.getElementById("pairSounds-" + index + "-word2_id");
        // IF input field has data/value whatever its called
        
        
        var groupindex = w2idfield.dataset.groupindex;
        if (groupindex) {
            s1inputfield.classList.add("suggests1");
            s1inputfield.dataset.groupindex = groupindex;
        }
        else {
            thing.classList.add("fillme");
        }

    });
    $( ".suggests1" ).change(function() {
        var target_group_index = $(this).data("groupindex");
        var typed_text = $(this).val();
        $(".suggests1").each(function() {
            var elem = $(this);
            console.log(elem.data("groupindex"));
            if (elem.data("groupindex") == target_group_index) {
                elem.val(typed_text);
            }
          });
    });

});



// For admin add for suggesting words to admin when adding with jquery chosen
let suggestion_indexes = [];

$("#pairs").on("chosen:showing_dropdown", function(e) {
// In dropdown: Highlight suggested words based on "suggested indexes" if any

    var words_in_dropdown = $("#pairs_chosen .active-result");
    words_in_dropdown.each(function( index ) {
        dropdown_index = parseInt($(this).attr("data-option-array-index"));
        // If the dropdown index is one of the suggested, set CSS class "suggested-result"
        if (suggestion_indexes.includes(dropdown_index)) {
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

// For admin add - chosen select
$('#pairs').on('change', function(evt, params) {
    console.log(params);
    console.log(params.selected);
// Ajax call to get suggested words based on selected ones and highlight them

    var selected_partner_ids = [];
    var selected_partner_elements = $("#pairs_chosen .search-choice a");
    var all_partners_elements = $("#pairs option");
    var all_ids_indexed = []
    var word1_id = $("#word1").val();
    
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
            word1_id : word1_id,
            chosen_ids : JSON.stringify(selected_partner_ids),
            all_indexes : JSON.stringify(all_ids_indexed)
        },
        url: url_for_suggested_pairs,
        type: "POST"

    }).done(function (data) {
        /* Suggested indexes is keeping track of which words in the dropdown to pull up */
        console.log("DATA:")
        if (typeof data["suggestion_indexes"] !== "undefined") {
            suggestion_indexes = data["suggestion_indexes"];
            suggested_ids = data["suggested_ids"];
            // If I regret auto-adding: remove "update_chosen_selection" and 
            // reenable display_suggested_words(...) which relies on suggested_idexes
            //display_suggested_words(suggestion_indexes);

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

    $('#pairs').val(updated_selection);
    $('#pairs').trigger('chosen:updated');
}


$(".delete-news-btn").click(function() {

    news_id = $(this).data("id");
    containing_news_card = $(this).parent().parent();

    $.ajax({
        data: {
            news_id : news_id
            //news_id : JSON.stringify(news_id)
        },
        url: url_for_delete_news,
        type: "POST"

    }).done(function (data) {
        /* Suggested indexes is keeping track of which words in the dropdown to highlight */
            console.log(data["message"]);
            if (data["message"] === "ok") {
                containing_news_card.remove();
            }
        });
  });

  $(".delete-group-btn").click(function() {

    group_id = $(this).data("id");
    if (confirm(`Really delete group ${group_id}?`)) {

        $.ajax({
            data: {
                group_id : group_id
            },
            url: url_for_delete_group,
            type: "POST"
            
        }).done(function (data) {
            /* Suggested indexes is keeping track of which words in the dropdown to highlight */
            console.log(data["message"]);
            if (data["message"] === "ok") {
                $("#div-group-" + group_id).remove();
            }
        });
    }
  });


  $(".btn-remove-from-group").click(function() {

    group_id = $(this).data("groupid");
    obj_id = $(this).data("objid");
    obj_string = $(this).data("objstring");
    obj_type = $(this).data("objtype");
    
    if (confirm(`Really delete '${obj_string}' from group ${group_id}?`)) {

        $.ajax({
            data: {
                group_id : group_id,
                obj_id : obj_id,
                obj_type : obj_type
            },
            url: url_for_remove_from_group,
            type: "POST"
            
        }).done(function (data) {
            /* Suggested indexes is keeping track of which words in the dropdown to highlight */
            console.log(data["message"]);
            if (data["message"] === "ok") {
                $(".badword-" + obj_id).remove();
            }
        });
    }
  });

  $(".isinitial-yn").change(function() {

    obj_id = $(this).data("objid");
    obj_type = $(this).data("objtype");
    typed_value = $(this).val();
    console.log(typed_value);

    if (typed_value === "y" || typed_value === "n") {
        console.log("yes or no, ajax");
        
        $.ajax({
            data: {
                obj_id : obj_id,
                typed_value: typed_value,
                obj_type: obj_type
            },
            url: url_for_set_initial,
            type: "POST"
            
        }).done(function (data) {
            /* Suggested indexes is keeping track of which words in the dropdown to highlight */
            console.log(data["message"]);
            if (data["message"] === "ok") {
                $(`#init-fix-${obj_type}-${obj_id}`).html("Fixed!");
            }
            else {
                $(`#init-fix-${obj_type}-${obj_id}`).html(data["message"]);
                $(`#init-fix-${obj_type}-${obj_id}`).css({"color": "red"});

            }
        });
    }
    else {
        $(this).css({"background-color": "yellow", "border": "2px solid red"});
        $(`#init-fix-${obj_type}-${obj_id}`).html("Y/N!");
    }

  });
