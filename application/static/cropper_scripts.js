// AJAX and JS funcitons for for adding custom images temporarily to collection,
// cropping them and uploading the cropped version all while keeping track of the
// word id.

// upload word id keeps track of what word the user is trying to give an image
let upload_word_id;
// image url keeps track of the url for the selected image (for loading cropper when cropper modal shows)
let cropper_img_url = "";

let global_cropper;

function set_upload_word_id(id) {
    console.log("Setting word id to " + id);
    $("#upload_word_id").attr("value",id);
    upload_word_id = id;
}

function fileSelected() {

    console.log("fileselected");

    var input_file_form = new FormData($('#upload-file')[0]);
    var files = $('#image')[0].files;
    
    // Check file selected or not
    if(files.length > 0 ){

        if (validate_image(files[0])) {
            console.log("image valid");
            show_cropper_modal();
        }
        else {
            console.log("image not valid");
        }
    }
}

// url_for_image_upload is defined in the macro for word card buttons since it's passed in from here
function upload_file(url_for_img_upload, image_file_form) {

    // Upload file to server and save if valid
    console.log("uploading file");
    $.ajax({
        type: 'POST',
        url: url_for_img_upload,
        data: image_file_form,
        contentType: false,
        cache: false,
        processData: false,
        success: function(data) {
            console.log('Hello file!');
        },
    }).done(function(data) {
        if (data.error) {
            console.log("file wasn't saved.");
            alert(data.error);
        }
        else {
            console.log("file has been saved");
            cropper_img_url = data.path;
        }
    }); // upload-file finished
}

// url_for_image_upload is defined in the macro for word card buttons since it's passed in from here
function validate_image(file) {

    console.log("file");
    var t = file.type.split('/').pop().toLowerCase();
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
    $("#croppermodal").modal("show");
    // when this modal is ready cropper is started
}

// on show modal start cropper (ot cropper won't load right)
$('#croppermodal').on('shown.bs.modal', function () {
    // your on click event binding here.
    console.log("showing bs modal");
    // example of triggering an input.
    $("#cropperimage").attr("src", cropper_img_url);
    start_cropper(cropper_img_url);
})

// on hide modal destroy cropper
$('#croppermodal').on('hidden.bs.modal', function () {
    console.log("modal closed");
    $("#image").html("");
    $("#image").val("");
    const image = document.getElementById('cropperimage');
    image.cropper.destroy();
    console.log("destroyed cropper");

});

// initialize cropper
function start_cropper(new_url) {
    const input = $("#image");
    console.log(input);
    const image = document.getElementById('cropperimage');
    const img_data = input[0].files[0];
    const liveurl = URL.createObjectURL(img_data);

    console.log("starting cropper");

    
    const cropper = new Cropper(image, {
        aspectRatio: 1 / 1,
        viewMode: 2,
        preview: $("#preview"),
        autoCropArea: 1,
        movable: false,
        rotatable: false,
        //scalable: false,
        //zoomable: false,
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
    image.cropper.replace(liveurl);
    console.log("real cropper: " + image.cropper);
    global_cropper = image.cropper;
    console.log("replaced image?");


}

// On pressing confirm button in modal
$("#cropper-confirm").click(function() {

    console.log("cropper confirm clicked");

    global_cropper.getCroppedCanvas().toBlob((blob) => {
        const image_form_data = new FormData();
        creimag.src = URL.createObjectURL(blob);
        image_form_data.append('file', creimag.src, 'blob.png');
        image_form_data.append('upload_word_id', upload_word_id);
        upload_file(url_for_img_upload, image_form_data);
    })
    $("#croppermodal").modal("hide");
});
// End of collection-related AJAX