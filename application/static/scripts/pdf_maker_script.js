/* 
TODO:
Lav build_lottery_boardgame funktion, som bruger game objekt
*/


var staticroot = "/static/" // Static root is needed for loading any images into any product
var game; // Will contain all information about game


// Determine important board game generation variables based on selected design and return a game (object)
// Insert variables for designs here!!
class Game {
    constructor(design) {
        this.design = design;
        this.listcount = 0;
        this.list_size = 0;
        this.filename = "";
        this.bgimg_path = "";
        this.fgimg_path = "";
        this.canvas_width = 0;
        this.canvas_height = 0;
        this.imagecount = 0;
        this.word_image_objects = []; // Is populated by ajax call when design selected/word count given

        switch(this.design) {
            case "solar":
                console.log("switch solar");
                this.listcount = 1;
                this.list_size = 30;
                this.filename = "solsystem_spilleplade";
                this.bgimg_path = staticroot + "boardgames/images/a3space_background.jpg";
                this.fgimg_path = staticroot + "boardgames/images/a3space_foreground.png";
                this.canvas_width = 3508; // A4 mm
                this.canvas_height = 2480; // A4 mm
    
                break;
            case "lottery-4":
                console.log("switch lottery 4")
                this.listcount = 4;
                this.list_size = 4;
                this.filename = "lotteri_med_4_billeder";
                this.bgimg_path = staticroot + "boardgames/images/lottery4_inka_background.png";
                // fgimg_path = 
                break;
            case "lottery-6":
                // code block
                this.listcount = 4;
                this.list_size = 6;
                this.filename = "lotteri_med_6_billeder";
                this.bgimg_path = staticroot + "boardgames/images/a3space_background.jpg";
                this.fgimg_path = staticroot + "boardgames/images/a3space_foreground.png";
                break;
            default:
                // code block
                console.log("switch case defaulted");
          }
          
          
        this.imagecount = this.listcount * this.list_size;

    }

    get image_paths(){
        var word_image_paths = []
        for(var i = 0; i < this.word_image_objects.length; i++) {
            var obj = staticroot + game.word_image_objects[i];
            word_image_paths.push(obj.path);
        }
        return word_image_paths;
        
    }
}


class Game_image {
    constructor(design) {
        this.x = 0;
        this.y = 0;
        this.degrees = 0;
        this.path = "";
        this.mask_path = "";

        switch(this.design) {
            case "solar":
    
                break;
            case "lottery-4":

                // fgimg_path = 
                break;
            case "lottery-6":
                // code block

                break;
            default:
                // code block
                console.log("switch case defaulted");
          }

    }
}

// Step 2: Initialize sortable based on selected board game design (this will affect what is shown in step 2)
// Sortable docs: https://api.jqueryui.com/sortable/ 
function initialize_sortable(game) {

    var design = game.design
    console.log("board game design is: " + design);


    // 1. Dynamically generate sortable with multiple lists (ids: sortable-0, sortable-1, sortable-2 ...)
    // For every list (fx lottery plate) add a new sortable with class connectedSortable)
    $("#step-2-sortable_wrapper").empty();
    $("#list_size").text(game.list_size);
    if (game.listcount === 1) {
        $(".sortable-feedback").hide();
    }
    else {
        $(".sortable-feedback").show();
    }
    for (var list_number = 0; list_number < game.listcount; ++ list_number) {
        console.log(this);
        var ul = $('<ul/>');
        ul.attr("id", "sortable-" + list_number)
        ul.addClass("connectedSortable");

        ul.sortable({
            update: function( event, ui ) {}, // So update event can be watched
            connectWith: ".connectedSortable", 
            update: function(){
                console.log("update");
            },
            // Long function in "stop" to reevaluate validity (list lengths) and enable/disable "next".
            stop: function(){
                console.log("stop");

                var allowed = true;
                $(".connectedSortable").each(function(index, obj){
                    listitems = $(obj).find("li");
                    if (listitems.length !== game.list_size) {
                        allowed = false;
                        $(obj).addClass("error");
                        $(".sortable-feedback").addClass("error");
                    }
                    else {
                        $(obj).removeClass("error");
                    }
                });
                if (!allowed) {
                    $(".sw-btn-next").prop( "disabled", true );
                }
                else {
                    $(".sw-btn-next").prop( "disabled", false );
                    $(".sortable-feedback").removeClass("error");
                }
            },

        }).disableSelection();

        $( "#step-2-sortable_wrapper" ).append(ul);
    }

};


// Generate DOM ul from word image objects
function put_words_in_DOM(game) {

    list_number = 0 // for keeping track of what list in loop
    list_max_size = game.list_size
    current_list_free_spaces = list_max_size

    $(game.word_image_objects).each(function(index){
        console.log(`Word ${index}, list ${list_number}, space left: ${current_list_free_spaces}`);
        sort = $("#sortable-" + list_number);
        var li = $("<li>", {"data-id": this.id});
        li.text(this.word);
        sort.append(li);
        current_list_free_spaces--;
        if (current_list_free_spaces === 0) {
            list_number ++
            current_list_free_spaces = list_max_size;
        }
    }); 
};


// Loads and returns an image. Use with await when an image needs to be loaded before continuing
function loadImage(src){
    return new Promise((resolve) => {
        image = new Image();
        image.src = src;
        image.onload = () => resolve(image);
    })
}


// Draws an image with specified size, coords and rotation on a canvas. Can be awaited.
async function drawImageToCtx(context, x, y, src, degrees, fullwidth=false, square_height_width=370) {
    /*Draws a given src to a given context at given coords - Only draws squares
    - which context
    - what coordinates
    - path to image/png mask
    - rotation
    - is it full width? Optional
    - height and width (same) of square. Optional. (Default is 370/solar size)
    */

    width = square_height_width;
    height = square_height_width;
    const loaded_image = await loadImage(src);

    if (fullwidth) {
        width = canvas.width;
        height = canvas.height;
    }

    if (degrees > 0) {
        // Save context. Set anchor point in the middle. Rotate canvas. Insert image. Rotate canvas back. Restore context.
        context.save();
        context.translate(x + width/2, y+height/2);
        context.rotate(degrees*Math.PI/180);
        context.drawImage(loaded_image, width/2 * (-1), height/2 * (-1), width, height);
        context.rotate(-(degrees*Math.PI/180));
        context.restore();
    }
    else {
        context.drawImage(loaded_image, x, y, width, height);
    }
}


// Takes a mask shape and an image and uses a temp context and an end context to draw them onto the end context ------ all designs
async function addMaskedImage(x, y, img_src, mask_src, degrees, end_context, temp_context) {

    // draw mask on temporary, empty canvas with given coordinates
    await drawImageToCtx(temp_context, x, y, mask_src, degrees);

    // draw image inside mask with same given coordinates
    temp_context.globalCompositeOperation = "source-in";
    await drawImageToCtx(temp_context, x, y, img_src, degrees);
    temp_context.globalCompositeOperation = "source-over";

    // Draw masked image on the "real" canvas - the whole canvas is drawn, therefore 0,0
    tmp_src = canvas_tmp.toDataURL();
    await drawImageToCtx(end_context, 0, 0, tmp_src, 0, true);

    // Clear temporary canvas for more drawing
    temp_context.clearRect(0, 0, canvas_tmp.width, canvas_tmp.height);

}


async function build_solar_board_game(end_context, temp_context){ // Only called if selected_game_design is "solar"

    word_image_paths = game.image_paths 
    $(".btn-loading").text("Placerer Merkur og Venus");

    // Draw background image
    await drawImageToCtx(end_context, 0, 0, game.bgimg_path, 0, true);
    
    // Draw all fields
    await addMaskedImage(130, 1950, word_image_paths[0], staticroot + "boardgames/images/mask-image1.png", 250, end_context, temp_context);
    await addMaskedImage(60, 1600, word_image_paths[1], staticroot + "boardgames/images/mask-image1.png", 265, end_context, temp_context);
    await addMaskedImage(60, 1240, word_image_paths[2], staticroot + "boardgames/images/mask-image3.png", 280, end_context, temp_context);
    $(".btn-loading").text("Placerer Jorden");
    await addMaskedImage(160, 880, word_image_paths[3], staticroot + "boardgames/images/mask-image1.png", 295, end_context, temp_context);
    await addMaskedImage(320, 560, word_image_paths[4], staticroot + "boardgames/images/mask-image3.png", 305, end_context, temp_context);
    await addMaskedImage(550, 250, word_image_paths[5], staticroot + "boardgames/images/mask-image2.png", 315, end_context, temp_context);
    $(".btn-loading").text("Placerer Mars");
    await addMaskedImage(860, 60, word_image_paths[6], staticroot + "boardgames/images/mask-image3.png", 340, end_context, temp_context);
    await addMaskedImage(1240, 10, word_image_paths[7], staticroot + "boardgames/images/mask-image1.png", 359, end_context, temp_context);
    await addMaskedImage(1630, 15, word_image_paths[8], staticroot + "boardgames/images/mask-image1.png", 2, end_context, temp_context);
    $(".btn-loading").text("Placerer Jupiter");
    await addMaskedImage(2010, 40, word_image_paths[9], staticroot + "boardgames/images/mask-image2.png", 10, end_context, temp_context);
    await addMaskedImage(2380, 130, word_image_paths[10], staticroot + "boardgames/images/mask-image3.png", 25, end_context, temp_context);
    await addMaskedImage(2720, 330, word_image_paths[11], staticroot + "boardgames/images/mask-image2.png", 35, end_context, temp_context);
    await addMaskedImage(3000, 575, word_image_paths[12], staticroot + "boardgames/images/mask-image3.png", 60, end_context, temp_context);
    await addMaskedImage(3090, 945, word_image_paths[13], staticroot + "boardgames/images/mask-image2.png", 89, end_context, temp_context);
    await addMaskedImage(3080, 1320, word_image_paths[14], staticroot + "boardgames/images/mask-image1.png", 100, end_context, temp_context);
    $(".btn-loading").text("Placerer Saturn");
    await addMaskedImage(2940, 1650, word_image_paths[15], staticroot + "boardgames/images/mask-image2.png", 130, end_context, temp_context);
    await addMaskedImage(2680, 1900, word_image_paths[16], staticroot + "boardgames/images/mask-image3.png", 155, end_context, temp_context);
    await addMaskedImage(2330, 2050, word_image_paths[17], staticroot + "boardgames/images/mask-image5.png", 170, end_context, temp_context);
    $(".btn-loading").text("Placerer Uranus");
    await addMaskedImage(1950, 2100, word_image_paths[18], staticroot + "boardgames/images/mask-image4.png", 175, end_context, temp_context);
    await addMaskedImage(1570, 2100, word_image_paths[19], staticroot + "boardgames/images/mask-image4.png", 185, end_context, temp_context);
    await addMaskedImage(1220, 1970, word_image_paths[20], staticroot + "boardgames/images/mask-image5.png", 215, end_context, temp_context);
    $(".btn-loading").text("Placerer Neptun");
    await addMaskedImage(940, 1710, word_image_paths[21], staticroot + "boardgames/images/mask-image3.png", 240, end_context, temp_context);
    await addMaskedImage(820, 1355, word_image_paths[22], staticroot + "boardgames/images/mask-image2.png", 270, end_context, temp_context);
    $(".btn-loading").text("Så blev det solens tur");
    await addMaskedImage(860, 999, word_image_paths[23], staticroot + "boardgames/images/mask-image5.png", 295, end_context, temp_context);
    await addMaskedImage(1110, 719, word_image_paths[24], staticroot + "boardgames/images/mask-image4.png", 320, end_context, temp_context);
    await addMaskedImage(1460, 590, word_image_paths[25], staticroot + "boardgames/images/mask-image5.png", 350, end_context, temp_context);
    await addMaskedImage(1820, 629, word_image_paths[26], staticroot + "boardgames/images/mask-image3.png", 370, end_context, temp_context);
    await addMaskedImage(2140, 770, word_image_paths[27], staticroot + "boardgames/images/mask-image2.png", 410, end_context, temp_context);
    await addMaskedImage(2260, 1100, word_image_paths[28], staticroot + "boardgames/images/mask-image3.png", 450, end_context, temp_context);
    await addMaskedImage(2160, 1440, word_image_paths[29], staticroot + "boardgames/images/mask-image5.png", 490, end_context, temp_context);
    $(".btn-loading").text("Færdig");

    
    // Draw foreground
    await drawImageToCtx(end_context, 0, 0, game.fgimg_path, 0, true);

}


// MANAGEING DATA IN BOARDGAME STEP WIZARD (smartwizard)
// Step 1: Get/set image objects based on selection
$(".selectable-theme").click(function(){
    elem =  $(this);
    var selected_game_design = elem.data("design"); // data-design can be: solar | lottery-4 | ...
    game = new Game(selected_game_design);
    
    // Get an (ordered) list of word image objects from server (user's collection) based on count
    $.ajax({
        url: "/ajax_get_boardgame_filenames", // Gets list of file names
        data: {
            count: game.imagecount
        },
        type: "POST",
    }).done(function(data) {
        // Store paths to objects in their own list
        // word image objects contain id, word and path
        $(".selected").removeClass("selected");
        elem.addClass("selected");
        elem.parent().addClass("selected");
        game.word_image_objects = JSON.parse(data);
        console.log(game.word_image_objects[0]);
        // Allow user to continue
        $(".sw-btn-next").prop( "disabled", false );
        
        initialize_sortable(game);
        console.log("put words in DOM called:");
        put_words_in_DOM(game);

    });
});

// When leaving a step update word_image_objects in the new order.
$("#smartwizard").on("leaveStep", function(e, anchorObject, stepIndex, stepDirection) {

    console.log("Leaving step. Implementing new order?");

    var sortedIDs = [];

    // Taking all sortable lists and combining to one array in order
    $(".connectedSortable").each(function(index, obj){
        partial_sortable_list = $(obj).sortable( "toArray", {attribute: "data-id"});
        sortedIDs = sortedIDs.concat(partial_sortable_list);
    });

    // Updating the list of word image objects to user's preferred order
    var new_word_image_objects = []

    $(sortedIDs).each(function() {

        var new_id = this;

        $(game.word_image_objects).each(function() {

            var word_obj = this;

            if (word_obj.id == new_id) {

                new_word_image_objects.push(word_obj);
                return false;

            }
        });
    });

    game.word_image_objects = new_word_image_objects;

});

// DRAW SPACE BOARD GAME WITH CANVAS
$("#make_boardgame_btn").click(async function(){

    if (game.word_image_objects.length > 0) {


        // game is already defined when clicking selectable theme

        // Set canvas size to landscape A4 dimensions and make context
        canvas = document.createElement('canvas');
        canvas.width=game.canvas_width; // A4 mm
        canvas.height=game.canvas_height; // A4 mm
        var end_ctx = canvas.getContext("2d");
        end_ctx.beginPath();
        
        // Create a temporary, similar canvas for generating stuff before putting it onto the real canvas ----- solar specific
        canvas_tmp = document.createElement('canvas');
        canvas_tmp.width=canvas.width;
        canvas_tmp.height=canvas.height;
        var tmp_ctx = canvas_tmp.getContext("2d");
    
    
    
        $("#make_boardgame_btn").prop('disabled', true);
        $(".btn-loading").show();
        $(".btn-ready").hide();

        // Insert check here to ensure that there is a canvas to return to the user?
        switch(game.design) {
            case "solar":
                console.log("building solar game");
                // Takes a list of 30 image paths and fits the images onto the solar board game image
                await build_solar_board_game(end_ctx, tmp_ctx);    
                break;
            case "lottery-4":
                console.log("building lottery-4, lalala");
                break;
            case "lottery-6":
                console.log("building lottery-6, lalala");
                break;
            default:
                console.log("No valid design");
                $("#make_boardgame_btn").prop('disabled', false);
                $(".btn-loading").hide();
                $(".btn-ready").show();
                $("#make_boardgame_btn").css('opacity', '1.0');
          }





    
        // Convert canvas to downloadable image and prompt user to save it
        var imgData = canvas.toDataURL("image/jpeg", 1.0);
        var pdf = new jsPDF('l', 'mm', [420, 297]);
        
        
        // If canvas is generated as an element programatically
        pdf.addImage(imgData, 'JPEG', 0, 0, 420, 297);
        
    
        var filename = prompt('Gem i "overførsler" som', game.filename);
        if (filename === null) {
            console.log("cancel");
        }
        else {
            pdf.save(filename + ".pdf");
        }
        $(canvas_tmp).remove();
        

        // Reenable make_boardgame_btn
        $("#make_boardgame_btn").prop('disabled', false);
        $(".btn-loading").hide();
        $(".btn-ready").show();
        $("#make_boardgame_btn").css('opacity', '1.0');
    
    }
});

// As soon as document is ready load the smart wizard where all the fun will take place
$(document).ready(function(){

    $('#smartwizard').smartWizard({
    selected: 0,
    theme: '',
    autoAdjustHeight:true,
    transitionEffect:'fade',
    showStepURLhash: false,
    });

    $(".sw-btn-next").prop( "disabled", true );
    
    if( /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ) {
        $( "<p style='color: grey;'>Rækkefølgen kan desværre ikke ændres på mobile enheder.</p>" ).insertBefore( "#sortable" );
       }

});

