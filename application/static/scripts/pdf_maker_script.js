/* 
TODO:
Gør så ord bliver byttet om eller i hvert fald, at der aldrig kommer et forkert antal ord i en af sortable listerne
Dette vil kræve ny kode, da sortable selv står for koden til at drag droppe
Gør så andre game designs designer andre games.
Omstrukturer click make boardgame btn?
 */



var board_game_design = "" // Can be set to solar | lottery-4 | ...
var word_image_objects = []; // Is populated by ajax call when design selected/word count given


// MANAGEING DATA IN BOARDGAME STEP WIZARD (smartwizard)
// Step 1: Get/set image objects based on selection
$(".selectable-theme").click(function(){
    elem =  $(this);
    board_game_design = $(this).data("design"); // data-design can be: solar | lottery-4 | ...
    game = getGameObject(board_game_design);
    
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
        word_image_objects = JSON.parse(data);
        // Allow user to continue
        $(".sw-btn-next").prop( "disabled", false );
        
        initialize_sortable(game);
        console.log("put words in DOM called:");
        put_words_in_DOM(word_image_objects, game);

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
    new_word_image_objects = []

    $(sortedIDs).each(function() {

        var new_id = this;

        $(word_image_objects).each(function() {

            var word_obj = this;

            if (word_obj.id == new_id) {

                new_word_image_objects.push(word_obj);
                return false;

            }
        });
    });

    word_image_objects = new_word_image_objects;

 });

// Determine important board game generation variables based on selected design and return a game (object)
// Insert variables for designs here!!
function getGameObject(selected_design) {

    var game = {
        design: selected_design,
        listcount: 0,
        list_size: 0,
        imagecount: 0,
    }
    switch(selected_design) {
        case "solar":
            console.log("switch solar");
            game.listcount = 1;
            game.list_size = 30;
            break;
        case "lottery-4":
            console.log("switch lottery 4")
            game.listcount = 4;
            game.list_size = 4;
            break;
        case "lottery-6":
            // code block
            game.listcount = 4;
            game.list_size = 6;
            break;
        default:
            // code block
            console.log("switch case defaulted");
      }
      game.imagecount = game.listcount * game.list_size;

    return game;

};

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
function put_words_in_DOM(word_image_objects, game) {

    list_number = 0 // for keeping track of what list in loop
    list_max_size = game.list_size
    current_list_free_spaces = list_max_size

    $(word_image_objects).each(function(index){
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





// DRAW SPACE BOARD GAME WITH CANVAS
$("#make_boardgame_btn").click(function(){

    console.log("Make board game clicked");

    var staticroot = "/static/"


    canvas = document.createElement('canvas');
    canvas.width=3508;
    canvas.height=2480;
    canvas_tmp = document.createElement('canvas');
    canvas_tmp.width=3508;
    canvas_tmp.height=2480;

    
    var end_ctx = canvas.getContext("2d");
    var tmp_ctx = canvas_tmp.getContext("2d");
    end_ctx.beginPath();
    
    // Promise to load image
    function loadImage(src){
        return new Promise((resolve) => {
            image = new Image();
            image.src = src;
            image.onload = () => resolve(image);
        })
    }
    
    console.log("Promise made");
    async function drawImageToCtx(context, x, y, src, degrees, fullwidth=false) {

        width = 370;
        height = 370;
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
    
    async function addMaskedImage(x, y, img_src, mask_src, degrees) {

        // draw mask on temporary canvas
        await drawImageToCtx(tmp_ctx, x, y, mask_src, degrees);

        // draw image inside mask
        tmp_ctx.globalCompositeOperation = "source-in";
        await drawImageToCtx(tmp_ctx, x, y, img_src, degrees);
        tmp_ctx.globalCompositeOperation = "source-over";

        // Draw masked image on the "real"" canvas
        tmp_src = canvas_tmp.toDataURL();
        await drawImageToCtx(end_ctx, 0, 0, tmp_src, 0, true);

        // Clear temporary canvas for more drawing
        tmp_ctx.clearRect(0, 0, canvas_tmp.width, canvas_tmp.height);

    }
    
    
    async function build_solar_board_game(word_image_paths){ // Only called if board_game_design is "solar"
        $(".btn-loading").text("Placerer Merkur og Venus");

        // Draw background image
        await drawImageToCtx(end_ctx, 0, 0, staticroot + "boardgames/images/a3space_background.jpg", 0, true);
        
        
        // Draw all fields
        await addMaskedImage(130, 1950, staticroot + word_image_paths[0], staticroot + "boardgames/images/mask-image1.png", 250);
        await addMaskedImage(60, 1600, staticroot + word_image_paths[1], staticroot + "boardgames/images/mask-image1.png", 265);
        await addMaskedImage(60, 1240, staticroot + word_image_paths[2], staticroot + "boardgames/images/mask-image3.png", 280);
        $(".btn-loading").text("Placerer Jorden");
        await addMaskedImage(160, 880, staticroot + word_image_paths[3], staticroot + "boardgames/images/mask-image1.png", 295);
        await addMaskedImage(320, 560, staticroot + word_image_paths[4], staticroot + "boardgames/images/mask-image3.png", 305);
        await addMaskedImage(550, 250, staticroot + word_image_paths[5], staticroot + "boardgames/images/mask-image2.png", 315);
        $(".btn-loading").text("Placerer Mars");
        await addMaskedImage(860, 60, staticroot + word_image_paths[6], staticroot + "boardgames/images/mask-image3.png", 340);
        await addMaskedImage(1240, 10, staticroot + word_image_paths[7], staticroot + "boardgames/images/mask-image1.png", 359);
        await addMaskedImage(1630, 15, staticroot + word_image_paths[8], staticroot + "boardgames/images/mask-image1.png", 2);
        $(".btn-loading").text("Placerer Jupiter");
        await addMaskedImage(2010, 40, staticroot + word_image_paths[9], staticroot + "boardgames/images/mask-image2.png", 10);
        await addMaskedImage(2380, 130, staticroot + word_image_paths[10], staticroot + "boardgames/images/mask-image3.png", 25);
        await addMaskedImage(2720, 330, staticroot + word_image_paths[11], staticroot + "boardgames/images/mask-image2.png", 35);
        await addMaskedImage(3000, 575, staticroot + word_image_paths[12], staticroot + "boardgames/images/mask-image3.png", 60);
        await addMaskedImage(3090, 945, staticroot + word_image_paths[13], staticroot + "boardgames/images/mask-image2.png", 89);
        await addMaskedImage(3080, 1320, staticroot + word_image_paths[14], staticroot + "boardgames/images/mask-image1.png", 100);
        $(".btn-loading").text("Placerer Saturn");
        await addMaskedImage(2940, 1650, staticroot + word_image_paths[15], staticroot + "boardgames/images/mask-image2.png", 130);
        await addMaskedImage(2680, 1900, staticroot + word_image_paths[16], staticroot + "boardgames/images/mask-image3.png", 155);
        await addMaskedImage(2330, 2050, staticroot + word_image_paths[17], staticroot + "boardgames/images/mask-image5.png", 170);
        $(".btn-loading").text("Placerer Uranus");
        await addMaskedImage(1950, 2100, staticroot + word_image_paths[18], staticroot + "boardgames/images/mask-image4.png", 175);
        await addMaskedImage(1570, 2100, staticroot + word_image_paths[19], staticroot + "boardgames/images/mask-image4.png", 185);
        await addMaskedImage(1220, 1970, staticroot + word_image_paths[20], staticroot + "boardgames/images/mask-image5.png", 215);
        $(".btn-loading").text("Placerer Neptun");
        await addMaskedImage(940, 1710, staticroot + word_image_paths[21], staticroot + "boardgames/images/mask-image3.png", 240);
        await addMaskedImage(820, 1355, staticroot + word_image_paths[22], staticroot + "boardgames/images/mask-image2.png", 270);
        $(".btn-loading").text("Så blev det solens tur");
        await addMaskedImage(860, 999, staticroot + word_image_paths[23], staticroot + "boardgames/images/mask-image5.png", 295);
        await addMaskedImage(1110, 719, staticroot + word_image_paths[24], staticroot + "boardgames/images/mask-image4.png", 320);
        await addMaskedImage(1460, 590, staticroot + word_image_paths[25], staticroot + "boardgames/images/mask-image5.png", 350);
        await addMaskedImage(1820, 629, staticroot + word_image_paths[26], staticroot + "boardgames/images/mask-image3.png", 370);
        await addMaskedImage(2140, 770, staticroot + word_image_paths[27], staticroot + "boardgames/images/mask-image2.png", 410);
        await addMaskedImage(2260, 1100, staticroot + word_image_paths[28], staticroot + "boardgames/images/mask-image3.png", 450);
        await addMaskedImage(2160, 1440, staticroot + word_image_paths[29], staticroot + "boardgames/images/mask-image5.png", 490);
        $(".btn-loading").text("Færdig");
        
        // Draw foreground
        await drawImageToCtx(end_ctx, 0, 0, staticroot + "boardgames/images/a3space_foreground.png", 0, true);
        var imgData = canvas.toDataURL("image/jpeg", 1.0);
        var pdf = new jsPDF('l', 'mm', [420, 297]);
        
        
        // If canvas is generated as an element programatically
        pdf.addImage(imgData, 'JPEG', 0, 0, 420, 297);
        

        var filename = prompt('Gem i "overførsler" som', "spilleplade_solsystem");
        if (filename === null) {
            console.log("cancel");
        }
        else {
            pdf.save(filename + ".pdf");
        }
        $(canvas_tmp).remove();

        $("#make_boardgame_btn").prop('disabled', false);
        $(".btn-loading").hide();
        $(".btn-ready").show();
        $("#make_boardgame_btn").css('opacity', '1.0');
        
    }

    console.log("Many async functions defined");

    if (word_image_objects.length === 0) {
        console.log("no collection");
    }
    else {
        $(this).prop('disabled', true);
        $(".btn-loading").show();
        $(".btn-ready").hide();
        word_image_paths = []
        for(var i = 0; i < word_image_objects.length; i++) {
            var obj = word_image_objects[i];
            word_image_paths.push(obj.path);
        }
        if (board_game_design == "solar") {
            build_solar_board_game(word_image_paths);
        }
        else {
            console.log("Wasn't solar");
            $("#make_boardgame_btn").prop('disabled', false);
            $(".btn-loading").hide();
            $(".btn-ready").show();
            $("#make_boardgame_btn").css('opacity', '1.0');
        }
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

