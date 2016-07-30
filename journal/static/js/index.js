$(document).ready(function () {
    $('.tag').click(function () {
        var tag = $(this).text();
        console.debug(tag)
        $('#post_text').append(' #'+ tag);
    });

    $('#sendButton').click(function () {
        var showData = $('#show-data');
        var post_text = $('#post_text').val().trim();
        var category = $('#category').val().trim();
        if (post_text.length==0) {
            showData.text("Insert post!");
        }else{

            $.ajax({
                type: 'POST',
                url: $CURRENT_COLLECTION,
                 data: JSON.stringify(
                     {"text": post_text,
                     "category": category,
                     "user": "valsdav"}),
                contentType: "application/json",
                dataType: 'json',
                success: function(data){
                    showData.text("Post created: " + data.post_created +
                            "\nTags: " + data.tags);
                }
            });
        }
    });

});
