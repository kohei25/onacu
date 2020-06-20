document.addEventListener('DOMContentLoaded', (event) => {

  var removeButton = document.getElementsByClassName('delete');
  var addButton = document.getElementById('add-url');

  addButton.addEventListener("click", addUrl);

  for(let i=0; i < removeButton.length; i ++){
    removeButton[i].addEventListener("click", removeUrl);
  }

  const getCookie = (name) => {
    if (document.cookie && document.cookie !== "") {
      for (const cookie of document.cookie.split(";")) {
        const [key, value] = cookie.trim().split("=");
        if (key === name) {
          return decodeURIComponent(value);
        }
      }
    }
  };
  const csrftoken = getCookie("csrftoken");

  function removeUrl(event) {
    console.log("remove will")
    let url_id = event.currentTarget.getAttribute('data-url')
    console.log(url_id)
    data = {
      "url_id": url_id,
    }
    url = location.href + "update/";
    fetch(url, {
      method: "DELETE",
      body: JSON.stringify(data),
      headers: {
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        "X-CSRFToken": csrftoken,
      },
    })
      .then((response) => response.json())
      .then((response) => window.location.reload())
      .catch((error) => console.log(error));
  }

  function addUrl(event) {
    event.preventDefault();
    var inputValue = document.getElementsByTagName('input')[0].value;
    var select = document.getElementById('content').value;
    data = {data: [{
      "content": select,
      "url": inputValue,
    }]};
    url = location.href + 'update/';
    postUrl(url, data);
  }

  function postUrl(url, data) {
    return fetch(url, {
      method: "POST",
      body: JSON.stringify(data),
      headers: {
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        "X-CSRFToken": csrftoken,
      },
    })
      .then((response) => response.json())
      .then((response) => window.location.reload())
      .catch((error) => console.log(error));
  }

},false);