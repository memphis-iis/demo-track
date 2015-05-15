// Application-wide javascript
// Note that code here can assume that both lodash and jQuery are present

//Initial startup actions to make our life easier
$(function(){
    //Handle bootstrap drop-downs
    $('.dropdown-toggle').dropdown();

    //Automatically set up jQuery DataTables if they have the right class
    $('.data-table').DataTable();

    //If form controls have an ID, but not a name - set their name attribute
    $("input, select, textarea, button, datalist, keygen, output").each(function(idx, val){
        var ele = $(val);
        if (_.isEmpty(ele.attr('name'))) {
            ele.attr('name', ele.attr('id'));
        }
    });

    //If a table cell requests truncation, then do so
    $("td.trunc-text").each(function(idx, ele){
        ele = $(ele);
        ele.text(_.trunc(_.trim(ele.text()), 30));
    });
});
