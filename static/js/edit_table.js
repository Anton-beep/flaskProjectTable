let flag_replacement = false;

function edit_cell(element) {
    let replacement_num;
    if (flag_replacement && element.innerText.length > 2) {
        $('#lesson_modal').modal();
        document.getElementById("teacher").disabled = false;
        document.getElementById("rep_teacher").hidden = false;
    } else if (!flag_replacement && element.innerText.split(' ')[0] !== 'ЗАМЕНА') {
        $('#lesson_modal').modal();
        document.getElementById("teacher").disabled = true;
        document.getElementById("rep_teacher").hidden = true;
    }

    let teacher = document.getElementById("header_" + element.id.split('_')[0]).innerText;
    let time = document.getElementById("row_" + element.id.split('_')[1]).innerText;

    document.getElementById("teacher").value = teacher;
    document.getElementById("rep_teacher").value = teacher;
    document.getElementById("time").value = time;
    if (flag_replacement) {
        if (element.innerText.split(' ')[0] === 'ЗАМЕНА') {
            replacement_num = 1
        } else {
            replacement_num = 0
        }
        document.getElementById("title_form").value = "Изменение/Создание замены";
    } else {
        if (element.innerText.split(' ')[0] === 'ЗАМЕНА') {
            replacement_num = 1
            document.getElementById("title_form").value = "Изменение замены на урок";
        } else {
            replacement_num = 0
            document.getElementById("title_form").value = "Изменение урока";
        }
    }
    if (element.innerText.length > 2) {
        let grade = element.innerText.split(' ')[replacement_num];
        let topic = element.innerText.split(' ')[1 + replacement_num];
        let cabinet = element.innerText.split(' ')[2 + replacement_num];
        document.getElementById("grade").value = grade;
        document.getElementById("topic").value = topic;
        document.getElementById("cabinet").value = cabinet;
    } else {
        document.getElementById("grade").value = "";
        document.getElementById("topic").value = "";
        document.getElementById("cabinet").value = "";
    }
}

function edit_flag_replacement(element) {
    flag_replacement = element.checked;
}

function send_data(data) {
    let xhr = new XMLHttpRequest();

    xhr.open("POST", '/', false);
    xhr.setRequestHeader('Content-Type', 'application/json');

    xhr.send(JSON.stringify(data));
    document.location.reload();
}

function delete_data() {
    let data;
    if (flag_replacement) {
        data = {
            'message': 'delete replacement',
            'time': document.getElementById("time").value,
            'teacher': document.getElementById("teacher").value
        }
    } else {
        data = {
            'message': 'delete lesson',
            'time': document.getElementById("time").value,
            'teacher': document.getElementById("teacher").value
        }
    }

    send_data(data);
}

function change_week() {
    let day_to_change = document.getElementById("set_date").value

    let data = {
        'message': 'new week',
        'day': day_to_change
    }

    send_data(data);
}