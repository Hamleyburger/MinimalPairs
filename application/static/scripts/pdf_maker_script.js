
// Space board game's image count is hard coded to 30 because of the design of the game board.

var board_image_count = 30
var board_game_design = "" // Can be set to "solar"
var word_image_objects = [];


// MANAGEING DATA IN BOARDGAME STEP WIZARD (smartwizard)
// Step 1: Get/set image objects based on selection
$(".selectable-theme").click(function(){
    elem =  $(this);
    count = $(this).data("count");
    board_game_design = $(this).data("design");
    // get word count and maybe board game path(?)
    board_image_count = $(this).data("count");
    
    // Get an (ordered) list of word image objects from server based on count
    $.ajax({
        url: "/ajax_get_boardgame_filenames", // Gets list of file names
        data: {
            count: board_image_count
        },
        type: "POST",
    }).done(function(data) {
        // Store paths to objects in their own list
        // word image objects contain id, word and path
        $(".selected").removeClass("selected");
        elem.addClass("selected");
        elem.parent().addClass("selected");
        word_image_objects = JSON.parse(data);
        put_words_in_DOM(word_image_objects);
        // Change theme
        $(".sw-btn-next").prop( "disabled", false );
    });
});

// When leaving a step update word_image_objects in the new order.
$("#smartwizard").on("leaveStep", function(e, anchorObject, stepIndex, stepDirection) {

    var sortedIDs = $( "#sortable" ).sortable( "toArray", {attribute: "data-id"});
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



// Step 2: User can sort and order list of image objects
// Sortable docs: https://api.jqueryui.com/sortable/ 


$("#sortable").sortable({
    //revert: true,
    update: function( event, ui ) {}, // So update event can be watched
});




// Generate DOM ul from word image objects
function put_words_in_DOM(list) {
    //<li data-id="{{ word.id }}" data-position="{{ loop.index }}">{{ word.word }}</li>

    sort = $("#sortable");
    sort.empty();

    $(list).each(function(index){
        console.log("appending " + this);
        var li = $("<li>", {"data-id": this.id});
        li.text(this.word);
        sort.append(li);
    });

};





// DRAW SPACE BOARD GAME WITH CANVAS
$("#make_boardgame_btn").click(function(){

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
            $("#make_boardgame_btn").prop('disabled', false);
            $(".btn-loading").hide();
            $(".btn-ready").show();
            $("#make_boardgame_btn").css('opacity', '1.0');
        }
    }

});


$(document).ready(function(){

    $('#smartwizard').smartWizard({
    selected: 0,
    theme: '',
    autoAdjustHeight:true,
    transitionEffect:'fade',
    showStepURLhash: false,
    });

    $(".sw-btn-next").prop( "disabled", true );
    // Disable step
    //$('#smartwizard').smartWizard("stepState", [1, 2], "disable");

});

