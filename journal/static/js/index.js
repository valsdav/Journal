$(document).ready(function () {
    $('.tag').click(function () {
        var tag = $(this).text();
        var post_text = $('#post_text')
        post_text.val(post_text.val() + ' #'+ tag);
        post_text.focus()
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
                url: CURRENT_COLLECTION,
                 data: JSON.stringify(
                     {"text": post_text,
                     "category": category,
                     "user": "valsdav"}),
                contentType: "application/json",
                dataType: 'json',
                success: function(data){
                    //adding the post to the list
                    element = '<div class="list-group-item row">'+
                        '<div class="col-md-9">'+
                            '<div class="row">'+data.text + '</div>'+
                            '<div class="row">'+
                                '<div class="btn-group" role="group">';
                    for (i in data.tags){
                        element +='<button type="button" class="btn btn-default">'+
                                data.tags[i]+ '</button>';
                    }
                    element += '</div></div>'+
                    '<div class ="row">'+
                        '<div class="btn-group" role="group" aria-label="...">';
                    for (j in data.props){
                        element +='<button type="button" class="btn btn-info">'+
                            j+'='+ data.props[j]+'</button>';
                    }
                    element+='</div></div></div>'+
                    '<div class="col-md-3 list-group">'+
                        '<a href="#" class="list-group-item active">'+ data.category+
                        '</a><a href="#" class="list-group-item">' + data.user +
                        '</a></div></div>';
                    showData.prepend(element);
                    //adding the tags
                    var tag_list = $('#tags-list');
                    for (i in data.tags){
                        tg = data.tags[i];
                        if (collection_tags.indexOf(tg)<0){
                            collection_tags.push(tg);
                            tag_list.append('<li><a class="btn btn-primary tag"'+
                            'href="#" role="button">'+ tg +'</a></li>');
                        }
                    }
                }
            });
        }
    });

});
