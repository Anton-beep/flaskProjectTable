function edit_user(element) {
    let row = element.id.split('_')[1];

    let row_data = [
        "name",
        "surname",
        "patronymic",
        "grade",
        "access_level",
        "token"
    ]

    document.getElementById("id_form").value = row.toString();

    for (let i = 0; i < row_data.length; i++) {
        if (document.getElementById("cell" + (i + 2).toString() + "_" + row).innerText !== "-") {
            document.getElementById(row_data[i]).value = document.getElementById("cell" + (i + 2).toString() + "_" + row).innerText;
        } else {
            document.getElementById(row_data[i]).value = ""
        }
    }
    $('#user_edit_modal').modal();
}

function send_data(data) {
    let xhr = new XMLHttpRequest();

    xhr.open("POST", '/users', false);
    xhr.setRequestHeader('Content-Type', 'application/json');

    xhr.send(JSON.stringify(data));
    document.location.reload(true);
}

function delete_data() {
    let data;

    let user_id = document.getElementById("id_form").value;

    data = {
        'message': 'delete user',
        'user': user_id
    }


    console.log(data);

    send_data(data);
}