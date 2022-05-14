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
        this.canvas_width = 0;
        this.canvas_height = 0;
        this.imagecount = 0; // Calculated programmatically after switch check is completed.
        this.word_image_objects = []; // Is populated by ajax call when design selected/word count given
        this.orientation = "l";
        this.square_img_size = 500; // Pixel size of custom added game images
        this.pages = [];
        this.game_images = [];
        

        switch(this.design) {
            case "solar":
                this.listcount = 1;
                this.list_size = 30;
                this.filename = "solsystem_spilleplade";
                this.canvas_width = 3508; // A4 px
                this.canvas_height = 2480; // A4 px
                this.orientation = "l"; // portrait
                this.square_img_size = 370;
                this.pages = [
                    // Page 1
                    new Page("boardgames/images/a3space_background.jpg", "boardgames/images/a3space_foreground.png", [
                        // Images on page 1 (hard coded positions)
                        new Game_image(130, 1950, 250, staticroot + "boardgames/images/mask-image1.png"),
                        new Game_image(60, 1600, 265, staticroot + "boardgames/images/mask-image1.png"),
                        new Game_image(60, 1240, 280, staticroot + "boardgames/images/mask-image3.png"),
                        new Game_image(160, 880, 295, staticroot + "boardgames/images/mask-image1.png"),
                        new Game_image(320, 560, 305, staticroot + "boardgames/images/mask-image3.png"),
                        new Game_image(550, 250, 315, staticroot + "boardgames/images/mask-image2.png"),
                        new Game_image(860, 60, 340, staticroot + "boardgames/images/mask-image3.png"),
                        new Game_image(1240, 10, 359, staticroot + "boardgames/images/mask-image1.png"),
                        new Game_image(1630, 15, 2, staticroot + "boardgames/images/mask-image1.png"),
                        new Game_image(2010, 40, 10, staticroot + "boardgames/images/mask-image2.png"),
                        new Game_image(2380, 130, 25, staticroot + "boardgames/images/mask-image3.png"),
                        new Game_image(2720, 330, 35, staticroot + "boardgames/images/mask-image2.png"),
                        new Game_image(3000, 575, 60, staticroot + "boardgames/images/mask-image3.png"),
                        new Game_image(3090, 945, 89, staticroot + "boardgames/images/mask-image2.png"),
                        new Game_image(3080, 1320, 100, staticroot + "boardgames/images/mask-image1.png"),
                        new Game_image(2940, 1650, 130, staticroot + "boardgames/images/mask-image2.png"),
                        new Game_image(2680, 1900, 155, staticroot + "boardgames/images/mask-image3.png"),
                        new Game_image(2330, 2050, 170, staticroot + "boardgames/images/mask-image5.png"),
                        new Game_image(1950, 2100, 175, staticroot + "boardgames/images/mask-image4.png"),
                        new Game_image(1570, 2100, 185, staticroot + "boardgames/images/mask-image4.png"),
                        new Game_image(1220, 1970, 215, staticroot + "boardgames/images/mask-image5.png"),
                        new Game_image(940, 1710, 240, staticroot + "boardgames/images/mask-image3.png"),
                        new Game_image(820, 1355, 270, staticroot + "boardgames/images/mask-image2.png"),
                        new Game_image(860, 999, 295, staticroot + "boardgames/images/mask-image5.png"),
                        new Game_image(1110, 719, 320, staticroot + "boardgames/images/mask-image4.png"),
                        new Game_image(1460, 590, 350, staticroot + "boardgames/images/mask-image5.png"),
                        new Game_image(1820, 629, 370, staticroot + "boardgames/images/mask-image3.png"),
                        new Game_image(2140, 770, 410, staticroot + "boardgames/images/mask-image2.png"),
                        new Game_image(2260, 1100, 450, staticroot + "boardgames/images/mask-image3.png"),
                        new Game_image(2160, 1440, 490, staticroot + "boardgames/images/mask-image5.png")
                    ])
                ]
                break;


            case "lottery-4":
                this.listcount = 4;
                this.list_size = 4;
                this.filename = "lotteri_med_4_billeder"; // What the user sees when saving
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

                this.pages = [
                    // page 1 - grid med billedkort
                    new Page("boardgames/images/lottery4_inka_card_frontside.png", "", [
                        new Game_image(221, 737, 0),
                        new Game_image(732, 737, 0),
                        new Game_image(1246, 737, 0),
                        new Game_image(1755, 737, 0),
                        new Game_image(221, 1246, 0),
                        new Game_image(732, 1246, 0),
                        new Game_image(1246, 1246, 0),
                        new Game_image(1755, 1246, 0),
                        new Game_image(221, 1759, 0),
                        new Game_image(732, 1759, 0),
                        new Game_image(1246, 1759, 0),
                        new Game_image(1755, 1759, 0),
                        new Game_image(221, 2269, 0),
                        new Game_image(732, 2269, 0),
                        new Game_image(1246, 2269, 0),
                        new Game_image(1755, 2269, 0)
                    ]),
                    // page 2 - billedkort baggrund
                    new Page("boardgames/images/lottery4_inka_card_backside.png", "", []),

                    // page 3 - lotteriplader
                    new Page("boardgames/images/lottery4_inka_background.png", "", [
                        new Game_image(x1, y1, 0),
                        new Game_image(x2, y1, 0),
                        new Game_image(x1, y2, 0),
                        new Game_image(x2, y2, 0),
                        new Game_image(x3, y1, 0),
                        new Game_image(x4, y1, 0),
                        new Game_image(x3, y2, 0),
                        new Game_image(x4, y2, 0),
                        new Game_image(x1, y3, 0),
                        new Game_image(x2, y3, 0),
                        new Game_image(x1, y4, 0),
                        new Game_image(x2, y4, 0),
                        new Game_image(x3, y3, 0),
                        new Game_image(x4, y3, 0),
                        new Game_image(x3, y4, 0),
                        new Game_image(x4, y4, 0)
                    ])
                ]
                // Image placement needs to be hard coded for each indivisual board game.
                break;


                case "lottery-6":
                    this.listcount = 4;
                    this.list_size = 6;
                    this.filename = "lotteri_med_6_billeder";
                    this.canvas_width = 2480; // A4 px
                    this.canvas_height = 3508; // A4 px
                    this.orientation = "p"; // portrait
                    this.square_img_size = 502;
    
                    var x1 = 478;
                    var x2 = 990;
                    var x3 = 1500;
                    
                    var y1 = 735;
                    var y2 = 1247;
                    var y3 = 1757;
                    var y4 = 2270;


                    var a1 = 420;
                    var a2 = 989;
                    var a3 = 1560;
                    
                    var b1 = 460;
                    var b2 = 1029;
                    var b3 = 1964;
                    var b4 = 2534;
    
                    this.pages = [
                        // page 1 - grid med billedkort 1-12
                        new Page("boardgames/images/lot6/imgsfront.jpg", "", [
                            new Game_image(x1, y1, 0),
                            new Game_image(x2, y1, 0),
                            new Game_image(x3, y1, 0),
                            new Game_image(x1, y2, 0),
                            new Game_image(x2, y2, 0),
                            new Game_image(x3, y2, 0),
                            new Game_image(x1, y3, 0),
                            new Game_image(x2, y3, 0),
                            new Game_image(x3, y3, 0),
                            new Game_image(x1, y4, 0),
                            new Game_image(x2, y4, 0),
                            new Game_image(x3, y4, 0),
                        ]),
                        // page 2 - billedkort baggrund
                        new Page("boardgames/images/lot6/imgsbg.jpg", "", []),

                        // page 3 - grid med billedkort 13-24
                        new Page("boardgames/images/lot6/imgsfront.jpg", "", [
                            new Game_image(x1, y1, 0),
                            new Game_image(x2, y1, 0),
                            new Game_image(x3, y1, 0),
                            new Game_image(x1, y2, 0),
                            new Game_image(x2, y2, 0),
                            new Game_image(x3, y2, 0),
                            new Game_image(x1, y3, 0),
                            new Game_image(x2, y3, 0),
                            new Game_image(x3, y3, 0),
                            new Game_image(x1, y4, 0),
                            new Game_image(x2, y4, 0),
                            new Game_image(x3, y4, 0),
                        ]),
                        // page 4 - billedkort baggrund
                        new Page("boardgames/images/lot6/imgsbg.jpg", "", []),
    
                        // page 5 - lotteriplader 1+2
                        new Page("boardgames/images/lot6/preblank1.jpg", "", [
                            new Game_image(a1, b1, 0),
                            new Game_image(a2, b1, 0),
                            new Game_image(a3, b1, 0),
                            new Game_image(a1, b2, 0),
                            new Game_image(a2, b2, 0),
                            new Game_image(a3, b2, 0),
                            new Game_image(a1, b3, 0),
                            new Game_image(a2, b3, 0),
                            new Game_image(a3, b3, 0),
                            new Game_image(a1, b4, 0),
                            new Game_image(a2, b4, 0),
                            new Game_image(a3, b4, 0),
                        ]),

                        // p6 blank
                        new Page("", "", []), // blank page

                        // page 7 - lotteriplader 3+4
                        new Page("boardgames/images/lot6/preblank2.jpg", "", [
                            new Game_image(a1, b1, 0),
                            new Game_image(a2, b1, 0),
                            new Game_image(a3, b1, 0),
                            new Game_image(a1, b2, 0),
                            new Game_image(a2, b2, 0),
                            new Game_image(a3, b2, 0),
                            new Game_image(a1, b3, 0),
                            new Game_image(a2, b3, 0),
                            new Game_image(a3, b3, 0),
                            new Game_image(a1, b4, 0),
                            new Game_image(a2, b4, 0),
                            new Game_image(a3, b4, 0),
                        ]),

                    ]
                    // Image placement needs to be hard coded for each indivisual board game.
                    break;


            default:
                // code block
                console.log("switch case defaulted");
          }
          
          
        this.imagecount = this.listcount * this.list_size;
    }


    set image_objects(word_image_objects){ // is set with "=" so the thing after "=" becomes argument

        this.word_image_objects = word_image_objects;
        // Populate each page's images with paths in the order of word_image_objects' paths
        var pages = this.pages;

        var addthis = 0;
        // For hver side, sæt det antal billeder ind i puljen, der kan være, hvis ikke den opbruges fortsættes pulje til næste side.
        for(var page_no=0; page_no < pages.length; page_no++) {
            var page_image_slots = pages[page_no].game_images;
            // For hvert slot til billeder på siden
            for(var img_slot_no=0; img_slot_no < page_image_slots.length; img_slot_no++) {
                var absolute_slot_no = img_slot_no + addthis;
                // img slot nr is for this page. Absolute is for the whole object list across multiple pages.
                var obj = game.word_image_objects[absolute_slot_no];
                var image_path = staticroot + obj.path;
                page_image_slots[img_slot_no].path = image_path;
                if (img_slot_no === page_image_slots.length-1) { // if end of loop

                    if (absolute_slot_no < game.word_image_objects.length - 1) {
                        // billedpulje ikke brugt op. Fortsæt med de næste på næste side.
                        addthis += page_image_slots.length;
                    }
                    else {
                        // billedpulje er brugt op
                        addthis = 0;
                    }
                    // Vi har fundet enden af slots korrekt. Nu skal vi tjekke om der er 
                    // flere billeder og i så fald starte med det rigtige tal i næste iteration.
                    // Ligeledes hvis vi også har nået enden af objects (length minus 1), skal 
                    // vi resette addthis.
                }
            }
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

class Page {

    constructor(bgpath="", fgpath="", game_images=[]) {

        this.bgpath = bgpath;
        this.fgpath = fgpath;
        this.game_images = game_images;

        if (bgpath !== "") {
            this.bgpath = staticroot + bgpath
        }

        if (fgpath !== "") {
            this.fgpath = staticroot + fgpath
        }
    }
}


// Step 2: Initialize sortable based on selected board game design (this will affect what is shown in step 2)
// Sortable docs: https://api.jqueryui.com/sortable/ 
function initialize_sortable(game) {

    var design = game.design

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
            // Long function in "stop" to reevaluate validity (list lengths) and enable/disable "next".
            stop: function(){

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


async function build_board_game(end_context, temp_context){ 

    canvas_image_data_list = []; // This is to be filled with "pages" image data and returned for pdf generation

    for (p = 0; p < game.pages.length; p++) {
        var page = game.pages[p];

        console.log("building page " + p);

        // Clear and refill canvas
        end_context.clearRect(0, 0, canvas.width, canvas.height);
        end_context.fillRect(0, 0, canvas.width, canvas.height);

        // Draw background image if any
        if(page.bgpath !== "") {
            await drawImageToCtx(end_context, 0, 0, page.bgpath, 0, true);
        }
        
        // Draw game images by their assigned coordinates. Game images are contained in Page objects.
        obs = page.game_images;
        for (i = 0; i < obs.length; i ++) {
            await addMaskedImage(obs[i].x, obs[i].y, obs[i].rot, obs[i].mask_path, obs[i].path, end_context, temp_context);
        }
        
        // Draw foreground image if any
        if(page.fgpath !== "") {
            // Draw foreground
            await drawImageToCtx(end_context, 0, 0, page.fgpath, 0, true);
            
        }
        
        // Convert canvas to downloadable image and prompt user to save it
        var imgData = canvas.toDataURL("image/jpeg", 0.6); // compression of quality 0.6

        canvas_image_data_list.push(imgData);

    }
    
    return canvas_image_data_list;

}


// MANAGEING DATA IN BOARDGAME STEP WIZARD (smartwizard)
// Step 1: Get/set image objects based on selection
$(".selectable-theme").click(function(){
    elem =  $(this);
    var selected_game_design = elem.data("design"); // data-design can be: solar | lottery-4 | ...
    game = new Game(selected_game_design);
    
    // Get an (ordered) list of word image objects from server (user's collection) based on necessary count defined in Game object
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

        game.image_objects = JSON.parse(data); // using "set image_objects" to set game.word_image_objects.

        // Allow user to continue
        $(".sw-btn-next").prop( "disabled", false );
        
        initialize_sortable(game);
        put_words_in_DOM(game);

    });
});

// When leaving a step update word_image_objects in the new order.
$("#smartwizard").on("leaveStep", function(e, anchorObject, stepIndex, stepDirection) {

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

        // Make canvases including a temporary one for the building process
        canvas = document.createElement('canvas');
        canvas.width=game.canvas_width; // A4 mm
        canvas.height=game.canvas_height; // A4 mm
        var end_ctx = canvas.getContext("2d");
        end_ctx.beginPath();
        end_ctx.fillStyle = "white";
        end_ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        canvas_tmp = document.createElement('canvas');
        canvas_tmp.width=canvas.width;
        canvas_tmp.height=canvas.height;
        var tmp_ctx = canvas_tmp.getContext("2d");
    
    
        // Show/hide feedback
        $("#make_boardgame_btn").prop('disabled', true);
        $(".btn-loading").show();
        $(".btn-ready").hide();

        // Make a list of canvas image data with "build_board_game" based on game object.
        var pages_image_datas = await build_board_game(end_ctx, tmp_ctx);  


        // PDF generation: Determine dimensions
        if (game.orientation === "l") {
            var w = 420; // landscape mm width
            var h = 297; // landscape mm height
        }
        else { // orientation is "p"
            var w = 297; // landscape mm width
            var h = 420; // landscape mm height            
        }

        // Open a new PDF
        var pdf = new jsPDF(game.orientation, 'mm', [w, h], true);


        // Convert canvas to downloadable pdf file and prompt user to save it
        for (i = 0; i < pages_image_datas.length; i++) {
            
            if (i > 0) {
                pdf.addPage([w, h], game.orientation);
            }
            
            var imgData = pages_image_datas[i];

            // If canvas is generated as an element programatically
            pdf.addImage(imgData, 'JPEG', 0, 0, w, h, "", "SLOW");

            

        }


        // Hide/show feedback when done building.
        $("#make_boardgame_btn").prop('disabled', false);
        $(".btn-loading").hide();
        $(".btn-ready").show();
        $("#make_boardgame_btn").css('opacity', '1.0');


        
        // Ask user to provide a filename and accept the download og the generated PDF
        var filename = prompt('Gem i "overførsler" som', game.filename);
        if (filename === null) {
        }
        else {
            pdf.save(filename + ".pdf");
        }
        $(canvas_tmp).remove();
        

    
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

