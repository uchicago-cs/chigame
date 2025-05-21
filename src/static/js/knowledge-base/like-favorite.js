
document.addEventListener("DOMContentLoaded", function () {
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    const likeSpan = document.getElementById("like-span");
    const likeIcon = document.getElementById("like-icon");
    const likeurl = likeSpan.getAttribute('data-like-url')
    const likeCount = document.getElementById('like-count')


    likeSpan.addEventListener("click", function () {
        console.log('Posting like to:', likeurl);
        fetch(likeurl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                'X-CSRFToken': csrftoken
            },
            mode: 'same-origin', // learn this code from django doc
            body: JSON.stringify({})
        })
        .then(response => {
            if (!response.ok) {
                throw new Error("Network response was not ok"); // double check this
            }
            return response.json();
        })
        .then(data => {
            if (data.liked) {
                likeIcon.classList.remove("heart-hollow");
                likeIcon.classList.add("heart-liked");
              } else {
                likeIcon.classList.remove("heart-liked");
                likeIcon.classList.add("heart-hollow");
              }
            likeCount.textContent = `${data.like_count} ♥`;
        })
    });
    });
