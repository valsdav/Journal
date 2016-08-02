$(document).ready(function () {
    //function that add a tag to the post-text
    var tag_click = function(){
        var tag = $(this).attr("tag");
        var post_text = $('#post_text')
        post_text.val(post_text.val() + ' #'+ tag);
        post_text.focus();
    }
    //function to select the category in the searchbar dropdown menu
    var cat_query_click = function(){
        var cat = $(this).attr("cat");
        var cat_sel = $('#cat-selected');
        var previous_cat = cat_sel.attr("cat");
        cat_sel.text(cat + ' ('+ categories_tags[cat]+ ')');
        cat_sel.attr("cat", cat);
        if (previous_cat!="ALL" && cat=="ALL"){
            cat_sel.removeClass("btn-info");
            cat_sel.addClass("btn-success");
        }else if(previous_cat=="ALL" && cat!="ALL"){
            cat_sel.removeClass("btn-success");
            cat_sel.addClass("btn-info");
        }
        //a new query is triggered
        query_data(current_query);
    }
    //event handler for tag click in the posts. It adds
    //the tag in the search bar
    var tag_query_click = function (){
        var tg = $(this).text();
        var query_text = $('#query-text');
        query_text.val(query_text.val() + ' ' + tg);
        current_query = query_text.val().trim();
        query_data(current_query);
    }

    //adding event handler to add tags to post-test
    $('.add-tag').click(tag_click);
    //category management in the search bar
    $('.cat-query').click(cat_query_click);
    //click of tags in the post adds the tag to the search bar
    $('.query-tag').click(tag_query_click);

    //function that creates element for post
    var create_post_element = function(post){
        element = '<div class="list-group-item row">'+
            '<div class="col-md-9">'+
                '<div class="row">'+post.text + '</div>'+
                '<div class="row">'+
                    '<div class="btn-group" role="group">';
        for (j in post.tags){
            element+= '<button class="btn btn-default query-tag">'+
                        post.tags[j] + '</button>';
        }
        element += '</div></div>'+
        '<div class ="row">'+
            '<div class="btn-group" role="group" aria-label="...">';
        for (k in post.props){
            element +='<button type="button" class="btn btn-info">'+
                k+'='+ post.props[k]+'</button>';
        }
        element+='</div></div></div>'+
        '<div class="col-md-3 list-group">'+
            '<a href="#" class="list-group-item active">'+ post.category+
            '</a><a href="#" class="list-group-item">' + post.user +
            '</a></div></div>';
        return element;
    }

    //send data for new post
    $('#sendButton').click(function () {
        var post_list = $('#post-list');
        var post_text = $('#post_text').val().trim();
        var category = $('#category-input').val().trim();
        if (post_text.length==0) {
            post_list.text("Insert post!");
        }else{
            if (category.length==0){
                category="main";
            }
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
                    //adding the tags
                    var tag_list = $('#tags-list');
                    for (i in data.tags){
                        tg = data.tags[i];
                        if (!(tg in collection_tags)){
                            collection_tags[tg] = 1
                            tag_list.append('<li><a class="btn btn-primary add-tag"'+
                            'href="#" role="button" tag="'+tg + '">'+ tg +
                            '<span class="badge" tag="'+tg +'">'+1+ '</span></a></li>');
                            $('.add-tag[tag="'+tg+'"]').click(tag_click);
                        }else{
                            var badge = $("span[tag='"+ tg+ "']");
                            badge.text(parseInt(badge.text())+1);
                        }
                    }
                    //adding the category
                    if (!(category in categories_tags)){
                        categories_tags[category] = 1;
                        $('#cats-dropdown').prepend('<li><a href="#" cat="'+
                        category + '" class="cat-query">'+ category + ' ('+
                            categories_tags[category]+')' +'</a></li>');
                        $('.cat-query[cat="'+category+'"]').click(cat_query_click);
                    }else{
                        //catching the right li
                        categories_tags[category] += 1;
                        $('.cat-query[cat="'+category+'"]').text(category +
                                ' ('+ categories_tags[category] + ')');
                    }
                    //empty the post_text form and category
                    $('#post_text').val('');
                    $('#category-input').val('');
                    //triggering the query
                    query_data(current_query);
                }
            });
        }
    });


    //function to query posts
    var query_data = function(query){
        $.ajax({
            type: 'POST',
            url: CURRENT_COLLECTION+'/query',
             data: JSON.stringify(
                 {"query": query,
                 "category": $('#cat-selected').attr("cat"),
                 "user": "valsdav",
                 "limit":20}),
            contentType: "application/json",
            dataType: 'json',
            success: function(data){
                var post_list = $('#post-list');
                post_list.empty();
                for(var i = 0; i< data.length; i++){
                    var post = data[i];
                    var element = create_post_element(post);
                    post_list.append(element);
                }
                //adding event handler for tag in the post-list
                $('.query-tag').click(tag_query_click);
            }
        });
    }

    //searchbar input
    var current_query = '';
    $('#query-text').on('input',function(e){
        var q = $(this).val().trim();
        if(q!=current_query){
            current_query = q;
            query_data(current_query);
        }
    });


});
