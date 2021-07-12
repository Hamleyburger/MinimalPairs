// AJAX and JS funcitons for for adding custom images temporarily to collection,
// cropping them and uploading the cropped version all while keeping track of the
// url_fors are defined in the templates where they're used.

// upload word id keeps track of word
let upload_word_id;
// Let cropper be accessible from various functions and event listeners
let global_cropper;

function set_upload_word_id(id) {

    $("#upload_word_id").attr("value",id);
    upload_word_id = id;
}

function fileSelected() {
    // Show cropper modal if there is a valid file

    var files = $('#image')[0].files;

    if(files.length > 0 ){
        if (prevalidate_image(files[0])) {
            show_cropper_modal();
        }
    }
}


function update_wordcard_img(newpath) {

    let this_image_url = newpath;

    // loop over word cards and change path on the one with similar word id
    $('.card-img-top').each(function(i, obj) {
        element_wordid = $(this).attr("data-image-wordid");
        if (element_wordid === upload_word_id) {
            // Add random unique query string to make sure image is updated
            unique = Math.random();
            $(this).attr("src", this_image_url + '?' + unique);
        }
    }); 
}


function upload_file(url_for_img_upload, image_file_form) {

    // Attempt to upload file to server
    $.ajax({

        type: 'POST',
        url: url_for_img_upload,
        data: image_file_form,
        contentType: false,
        cache: false,
        processData: false,

    }).done(function(data) {

        if (data.error) {
            alert("File not saved. The file must be less than 3 MB and be .jpeg or .png");
        }
        else {
            update_wordcard_img(data.path);
        }

    }); // upload-file finished
}

function getType(file) {
    var t = file.type.split('/').pop().toLowerCase();
    if (t.toUpperCase() === "JPEG".toUpperCase() || t.toUpperCase() === "JPG".toUpperCase()) {
        return "jpeg";
    }
    else if (t.toUpperCase() === "PNG".toUpperCase()) {
        return "png";
    }
    else {
        return t
    }
}

function prevalidate_image(file) {

    // This is here to save the user from wasting time on cropping images that won't get accepted by the server anyway
    var t = getType(file);

    if (t != "jpeg" && t != "jpg" && t != "png") {
        alert('File must be .png or .jpg');
        document.getElementById("image").value = '';
        return false;
    }

    if (file.size > (3000000)) {
        alert('File size must be less than 3MB');
        document.getElementById("image").value = '';
        return false;
    }

    return true;

}

function show_cropper_modal() {
    // when this modal is ready and shown cropper is started
    $("#croppermodal").modal("show");
}

// on show modal start cropper (ot cropper won't load right)
$('#croppermodal').on('shown.bs.modal', function () {
    // Cropper is always in modal and modal does not exist without cropper
    start_cropper();
})

// on hide modal destroy cropper
$('#croppermodal').on('hidden.bs.modal', function () {

    $("#image").html("");
    $("#image").val("");
    const image = document.getElementById('cropperimage');
    image.cropper.destroy();

});

// initialize cropper
function start_cropper() {

    const image = document.getElementById('cropperimage'); // Define cropper element
    const input = $("#image"); // Get input field
    const img_data = input[0].files[0]; // Get image from input field
    const image_url = URL.createObjectURL(img_data); // Make URL for image

    
    const cropper = new Cropper(image, {

        aspectRatio: 1 / 1,
        viewMode: 2,
        preview: $("#preview"),
        autoCropArea: 1,
        movable: false,
        rotatable: false,

    });

    // Make sure image is replaced every time start_cropper is called
    image.cropper.replace(image_url);
    global_cropper = image.cropper;


}

// Confirm buttons saves image and closes cropper
$("#cropper-confirm").click(function() {

    var file = $('#image')[0].files[0];
    var filetype = getType(file);
    var mimetype = "image/" + filetype
    var filename = "x." + filetype // Server does not like extensionless files


    global_cropper.getCroppedCanvas().toBlob((blob) => {

        const image_form_data = new FormData();
        image_form_data.append('file', blob, filename);
        image_form_data.append('upload_word_id', upload_word_id);
        upload_file(url_for_img_upload, image_form_data);


    },
    mimetype
    );

    // Hiding modal triggers destruction of cropper
    $("#croppermodal").modal("hide");

});
