var staticroot = "/static/" // Static root is needed for loading any images into any product
var game; // Will contain all information about game
var canvas;
var canvas_tmp;

// Determine important board game generation variables based on selected design and return a game (object)
// Insert variables for designs here!!
// Use bg_test.html to adjust parametres to fit and hard code.
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
        this.game_images = [];
        this.word_image_objects = []; // Is populated by ajax call when design selected/word count given
        this.orientation = "l";

        switch(this.design) {
            case "solar":
                console.log("switch solar");
                this.listcount = 1;
                this.list_size = 30;
                this.filename = "solsystem_spilleplade";
                this.bgimg_path = staticroot + "boardgames/images/a3space_background.jpg";
                this.fgimg_path = staticroot + "boardgames/images/a3space_foreground.png";
                this.canvas_width = 3508; // A4 px
                this.canvas_height = 2480; // A4 px
                this.orientation = "l"; // portrait
                this.square_img_size = 370;



                // Image placement needs to be hard coded for each indivisual board game.
                this.game_images[0] = new Game_image(130, 1950, 250, staticroot + "boardgames/images/mask-image1.png");
                this.game_images[1] = new Game_image(60, 1600, 265, staticroot + "boardgames/images/mask-image1.png");
                this.game_images[2] = new Game_image(60, 1240, 280, staticroot + "boardgames/images/mask-image3.png");
                this.game_images[3] = new Game_image(160, 880, 295, staticroot + "boardgames/images/mask-image1.png");
                this.game_images[4] = new Game_image(320, 560, 305, staticroot + "boardgames/images/mask-image3.png");
                this.game_images[5] = new Game_image(550, 250, 315, staticroot + "boardgames/images/mask-image2.png");
                this.game_images[6] = new Game_image(860, 60, 340, staticroot + "boardgames/images/mask-image3.png");
                this.game_images[7] = new Game_image(1240, 10, 359, staticroot + "boardgames/images/mask-image1.png");
                this.game_images[8] = new Game_image(1630, 15, 2, staticroot + "boardgames/images/mask-image1.png");
                this.game_images[9] = new Game_image(2010, 40, 10, staticroot + "boardgames/images/mask-image2.png");
                this.game_images[10] = new Game_image(2380, 130, 25, staticroot + "boardgames/images/mask-image3.png");
                this.game_images[11] = new Game_image(2720, 330, 35, staticroot + "boardgames/images/mask-image2.png");
                this.game_images[12] = new Game_image(3000, 575, 60, staticroot + "boardgames/images/mask-image3.png");
                this.game_images[13] = new Game_image(3090, 945, 89, staticroot + "boardgames/images/mask-image2.png");
                this.game_images[14] = new Game_image(3080, 1320, 100, staticroot + "boardgames/images/mask-image1.png");
                this.game_images[15] = new Game_image(2940, 1650, 130, staticroot + "boardgames/images/mask-image2.png");
                this.game_images[16] = new Game_image(2680, 1900, 155, staticroot + "boardgames/images/mask-image3.png");
                this.game_images[17] = new Game_image(2330, 2050, 170, staticroot + "boardgames/images/mask-image5.png");
                this.game_images[18] = new Game_image(1950, 2100, 175, staticroot + "boardgames/images/mask-image4.png");
                this.game_images[19] = new Game_image(1570, 2100, 185, staticroot + "boardgames/images/mask-image4.png");
                this.game_images[20] = new Game_image(1220, 1970, 215, staticroot + "boardgames/images/mask-image5.png");
                this.game_images[21] = new Game_image(940, 1710, 240, staticroot + "boardgames/images/mask-image3.png");
                this.game_images[22] = new Game_image(820, 1355, 270, staticroot + "boardgames/images/mask-image2.png");
                this.game_images[23] = new Game_image(860, 999, 295, staticroot + "boardgames/images/mask-image5.png");
                this.game_images[24] = new Game_image(1110, 719, 320, staticroot + "boardgames/images/mask-image4.png");
                this.game_images[25] = new Game_image(1460, 590, 350, staticroot + "boardgames/images/mask-image5.png");
                this.game_images[26] = new Game_image(1820, 629, 370, staticroot + "boardgames/images/mask-image3.png");
                this.game_images[27] = new Game_image(2140, 770, 410, staticroot + "boardgames/images/mask-image2.png");
                this.game_images[28] = new Game_image(2260, 1100, 450, staticroot + "boardgames/images/mask-image3.png");
                this.game_images[29] = new Game_image(2160, 1440, 490, staticroot + "boardgames/images/mask-image5.png");

                console.log(this.game_images);
    
                break;
            case "lottery-4":
                console.log("switch lottery 4")
                this.listcount = 4;
                this.list_size = 4;
                this.filename = "lotteri_med_4_billeder";
                this.bgimg_path = staticroot + "boardgames/images/lottery4_inka_background.png";
                this.fgimg_path = "";
                this.canvas_width = 2480; // A4 px
                this.canvas_height = 3508; // A4 px
                this.orientation = "p"; // portrait
                this.square_img_size = 502;

                var x1 = 86;
                var x2 = 653;
                var x3 = 1323;
                var x4 = 1897;
                var y1 = 598;
                var y2 = 1168;
                var y3 = 1838;
                var y4 = 2408;
                // Image placement needs to be hard coded for each indivisual board game.
                this.game_images[0] = new Game_image(x1, y1, 0);
                this.game_images[1] = new Game_image(x2, y1, 0);
                this.game_images[2] = new Game_image(x1, y2, 0);
                this.game_images[3] = new Game_image(x2, y2, 0);
                this.game_images[4] = new Game_image(x3, y1, 0);
                this.game_images[5] = new Game_image(x4, y1, 0);
                this.game_images[6] = new Game_image(x3, y2, 0);
                this.game_images[7] = new Game_image(x4, y2, 0);

                this.game_images[8] = new Game_image(x1, y3, 0);
                this.game_images[9] = new Game_image(x2, y3, 0);
                this.game_images[10] = new Game_image(x1, y4, 0);
                this.game_images[11] = new Game_image(x2, y4, 0);
                this.game_images[12] = new Game_image(x3, y3, 0);
                this.game_images[13] = new Game_image(x4, y3, 0);
                this.game_images[14] = new Game_image(x3, y4, 0);
                this.game_images[15] = new Game_image(x4, y4, 0);

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
            var obj = game.word_image_objects[i];
            var image_path = staticroot + obj.path;
            word_image_paths.push(image_path);
        }
        return word_image_paths; 
    }

    set image_objects(word_image_objects){
        this.word_image_objects = word_image_objects;
        for(var i = 0; i < this.word_image_objects.length; i++) {
            var obj = game.word_image_objects[i];
            var image_path = staticroot + obj.path;
            this.game_images[i].path = image_path;
        }
    }
}


class Game_image {
    constructor(x, y, rot, mask_path="") {
        this.x = x;
        this.y = y;
        this.rot = rot;
        this.mask_path = mask_path;
        this.path = ""; // populate after worg_image_objects have been retrieved.
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
        // console.log(`Word ${index}, list ${list_number}, space left: ${current_list_free_spaces}`);
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
async function drawImageToCtx(context, x, y, src, degrees, fullwidth=false, square_height_width=game.square_img_size) {
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
async function addMaskedImage(x, y, degrees, mask_src, img_src, end_context, temp_context) {

    if(mask_src !== "") {

        // draw mask on temporary, empty canvas with given coordinates
        await drawImageToCtx(temp_context, x, y, mask_src, degrees);
        
        // draw image inside mask with same given coordinates
        temp_context.globalCompositeOperation = "source-in";
    }


    await drawImageToCtx(temp_context, x, y, img_src, degrees);
    temp_context.globalCompositeOperation = "source-over";

    // Draw masked image on the "real" canvas - the whole canvas is drawn, therefore 0,0
    tmp_src = canvas_tmp.toDataURL();
    await drawImageToCtx(end_context, 0, 0, tmp_src, 0, true);

    // Clear temporary canvas for more drawing
    temp_context.clearRect(0, 0, canvas_tmp.width, canvas_tmp.height);

}


async function build_board_game(end_context, temp_context){ // Only called if selected_game_design is "solar"

    word_image_paths = game.image_paths;
    // Draw background image
    await drawImageToCtx(end_context, 0, 0, game.bgimg_path, 0, true);
    
    obs = game.game_images;
    for (i = 0; i < obs.length; i ++) {
        await addMaskedImage(obs[i].x, obs[i].y, obs[i].rot, obs[i].mask_path, obs[i].path, end_context, temp_context);
        $(".btn-loading").text(i);
    }

    if(game.fgimg_path !== "") {
        // Draw foreground
        await drawImageToCtx(end_context, 0, 0, game.fgimg_path, 0, true);

    }

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
        game.image_objects = JSON.parse(data);
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

    console.log("Leaving step. Updating order.");

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

    game.image_objects = new_word_image_objects;

});

// Load images from server and make game object when button is clicked
$("#make_boardgame_btn").click(async function(){

    if (game.word_image_objects.length > 0) {


        // game is already defined when clicking selectable theme

        // Set canvas size to landscape A4 dimensions and make context
        canvas = document.createElement('canvas');
        canvas.width=game.canvas_width; // A4 mm
        canvas.height=game.canvas_height; // A4 mm
        var end_ctx = canvas.getContext("2d");
        end_ctx.beginPath();
        end_ctx.fillStyle = "white";
        end_ctx.fillRect(0, 0, canvas.width, canvas.height);
        
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
                await build_board_game(end_ctx, tmp_ctx);    
                break;
            case "lottery-4":
                console.log("building lottery-4, lalala");
                await build_board_game(end_ctx, tmp_ctx);  
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

        if (game.orientation === "l") {
            var w = 420; // landscape mm width
            var h = 297; // landscape mm height
        }
        else { // orientation is "p"
            var w = 297; // landscape mm width
            var h = 420; // landscape mm height            
        }


        var pdf = new jsPDF(game.orientation, 'mm', [w, h]);
        // If canvas is generated as an element programatically
        pdf.addImage(imgData, 'JPEG', 0, 0, w, h);
        
    
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

// Start SmartWizard - as soon as document is ready load the smart wizard where all the fun will take place
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

