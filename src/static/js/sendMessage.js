function sendMessage(){
    var message = document.getElementById("message").value;
    const email = document.getElementById("email").value;
    const tID = document.getElementById("tID").value;
    const csrfToken = document.getElementsByName('csrfmiddlewaretoken')[0].value;

    if (message != "") {

        var messageData ={
            "sender": email,
            "content": message,
            "update_on": null,
            "tournament": tID
        }

        fetch("http://127.0.0.1:8000/api/tournaments/chat/", {
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(messageData),
        })

    }

    console.log(messageData);
    document.getElementById("message").value = "";
}
