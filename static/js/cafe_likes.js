"use strict";

const PORT = 5001;
const BASE_URL = `http://localhost:${PORT}/`; // always needs to match launch.json url
// const BASE_URL = `http://127.0.0.1:${PORT}/`;

const $likeMsgForms = $("form[data-cafe-id]");

$(async function () {
  const response = await axios({
    url: `${BASE_URL}/api/likes`,
    // url: `${BASE_URL}/api/likes/${cafe_id}`,
    method: "GET",
    params: { cafe_id: cafeId },
  });
  let result = response.data;

  let likes = result.likes;
  processStatusBool(likes);
});

async function toggleLikeCafe(cafe_id) {
  const response = await axios({
    url: `${BASE_URL}/api/toggle_like/${cafe_id}`,
    method: "POST",
  });
  let result = response.data;

  console.log("CONSOLELOG: ", response.data);

  processStatus(result);
}


$likeMsgForms.on("submit", function (e) {
  e.preventDefault();
  const cafeId = e.target.dataset.cafeId;
  toggleLikeCafe(cafeId);
});

function processStatusBool(resultData) {
  if (resultData === true) {
    showUnlikeButton();
  } else if (resultData === false) {
    showLikeButton();
  }
}

function processStatus(resultData) {
  if ("liked" in resultData) {
    showUnlikeButton();
  } else if ("unliked" in resultData) {
    showLikeButton();
  }
}

function showLikeButton() {
  $("#Like").show();
  $("#Unlike").hide();
}

function showUnlikeButton() {
  $("#Unlike").show();
  $("#Like").hide();
}
