/*


    ADMIN SCRIPTS
    These scripts are only loaded when current user is authenticated (checked with jinja)


*/

// For admin add for suggesting words to admin when adding with jquery chosen
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

// For admin add - chosen select
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