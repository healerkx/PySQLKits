
function commitEntry(input) {
    var text = input.val().trim()
    if (this.currentText == text || text.length == 0) {
        return;
    }
    this.currentText = text;

    $.post('/entry', {content: text}, function(data) {
        if (data) {
            var result = eval("(" + data + ")");
        }
        var tr = input.attr('readonly', 'readonly').closest('tr').removeClass('new-entry');
        tr.find('a.begin').removeClass('disabled');
        window.location.reload();
    });
}

function addEntry(table, item) {
    var entry = table.find('thead tr.template')
        .clone().css('display', '');
    if (!item) {
        entry.addClass('new-entry');
    } else {
        // console.log(item);
        var input = entry.find('input');
        input.val(item['entry_content']).attr('readonly', 'readonly');

        var tr = input.closest('tr').attr('entry_id', item.entry_id).removeClass('new-entry');

        if (item.entry_status == 0) {
            tr.find('a.begin').removeClass('disabled')
        } else if (item.entry_status == 1) {
            tr.find('a.begin').css('display', 'none').closest('td').text(item.begin_time)
            tr.find('a.end-it').removeClass('disabled');
        } else if (item.entry_status == 2) {
            tr.find('a.begin').css('display', 'none').closest('td').text(item.begin_time)
            tr.find('a.end-it').css('display', 'none').closest('td').text(item.end_time)
        }
    }

    entry.appendTo(table.find('tbody'))
}

function showEntries(table, items)
{
    for (var i in items) {
        addEntry(table, items[i]);
    }
}

$(function () {

    var table = $('#main-table');

    $.get('/entries/today', function(data) {
        var items = eval('(' + data + ')');
        showEntries(table, items);
    });

    $('#add-todo').click(function() {
        var table = $('#main-table');
        if (table.find('.new-entry').length > 0) {
            return;
        }
        addEntry(table, null);
    });

    table.delegate('.entry-text', 'keypress', function(e) {
        if (e.ctrlKey && e.which == 13) {
            commitEntry($(this))
        }
    });

    table.delegate('a.begin', 'click', function () {
        var entryId = $(this).closest('tr').attr('entry_id');
        $.get('begin/entry/' + entryId, function (data) {
            if (data) {
                var result = eval("(" + data + ")");
                if (result['result'] == 1) {
                    // Here I reload the page to refresh the status
                    window.location.reload();
                }
            }
        })
    });

    table.delegate('a.end-it', 'click', function () {
        var entryId = $(this).closest('tr').attr('entry_id');
        $.get('end/entry/' + entryId, function (data) {
            if (data) {
                var result = eval("(" + data + ")");
                if (result['result'] == 1) {
                    // Here I reload the page to refresh the status
                    window.location.reload();
                }
            }
        })
    });
});