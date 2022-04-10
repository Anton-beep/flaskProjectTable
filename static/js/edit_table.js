function edit_cell(element) {
    $('#exampleModalCenter').modal();

    let replacement_num = 0

    let teacher = document.getElementById("header_" + element.id.split('_')[0]).innerText
    let time = document.getElementById("row_" + element.id.split('_')[1]).innerText

    document.getElementById("teacher").value = teacher
    document.getElementById("time").value = time
    if (element.innerText.split(';')[0] === 'ЗАМЕНА') {
        replacement_num = 1
        document.getElementById("ModalLongTitle").innerText = "Изменение замены на урок"
    } else {
        document.getElementById("ModalLongTitle").innerText = "Изменение урока"
    }
    if (element.innerText.length > 2) {
        let grade = element.innerText.split(';')[replacement_num]
        let topic = element.innerText.split(';')[1 + replacement_num]
        let cabinet = element.innerText.split(';')[2 + replacement_num]
        document.getElementById("grade").value = grade
        document.getElementById("topic").value = topic
        document.getElementById("cabinet").value = cabinet
    } else {
        document.getElementById("grade").value = ""
        document.getElementById("topic").value = ""
        document.getElementById("cabinet").value = ""
    }
}

function delete_lesson() {
    let xhr = new XMLHttpRequest();

    xhr.open("POST", '/', true);
    xhr.setRequestHeader('Content-Type', 'application/json');

    let data = {
        'message': 'delete',
        'time': document.getElementById("time").value,
        'teacher': document.getElementById("teacher").value
    }

    console.log(data)
    xhr.send(JSON.stringify(data));
    document.location.reload(true);
}
