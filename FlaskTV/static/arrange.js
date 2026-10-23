$(function () {
    var enabled = $('#sortable1');
    var field = document.getElementById('content');

    function updateArrangement() {
        field.value = enabled.sortable('toArray').join(',');
    }

    $('#sortable1, #sortable2').sortable({
        connectWith: '.connectedSortable',
        update: updateArrangement
    }).disableSelection();

    updateArrangement();
    document.getElementById('arrange-form').addEventListener('submit', updateArrangement);
});
