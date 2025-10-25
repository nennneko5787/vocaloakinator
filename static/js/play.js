let iframeElement = null;
let token = null;

async function startAki(cfToken) {
  const response = await fetch("/api/aki/start", {
    method: "POST",
    headers: {
      "content-type": "application/json",
    },
    body: JSON.stringify({ cfToken }),
  });
  if (response.status != 201) {
    document.querySelector(".cf-turnstile").remove();
    const overlayMessage = document.getElementById("overlayMessage");

    overlayMessage.classList.remove("quote-39");
    overlayMessage.classList.add("quote-danger");
    overlayMessage.textContent =
      "ゲームの初期化に失敗しました。ページを再読込してください。";
  }

  document.querySelector(".overlay").remove();

  const jsonData = await response.json();

  token = jsonData.token;
  document.getElementById("question").textContent = jsonData.question;

  const progressBar = document.querySelector(".progress");
  progressBar.value = jsonData.progress * 100;
  progressBar.textContent = `${jsonData.progress * 100}%`;
}

async function answer(answer) {
  const response = await fetch("/api/aki/answer", {
    method: "POST",
    headers: {
      "content-type": "application/json",
    },
    body: JSON.stringify({ token, answer }),
  });

  const jsonData = await response.json();
  if (response.status != 200) {
    alert(`エラーが発生しました。: ${jsonData.detail}`);
  }

  const progressBar = document.querySelector(".progress");
  const question = document.getElementById("question");
  if (jsonData.detail == "SONG_DOESNT_MATCH") {
    question.textContent = jsonData.question;

    progressBar.value = jsonData.progress * 100;
    progressBar.textContent = `${jsonData.progress * 100}%`;
  } else if (jsonData.detail == "SONG_MATCHED") {
    document.querySelector(".buttons").remove();
    question.innerHTML = `おそらくその曲は${jsonData.song.musician}さんの${jsonData.song.name}でしょう！<br>\n<a href="${jsonData.song.link}">ここから聴くことができます</a>`;

    console.log(jsonData.song.link);
    if (jsonData.song.link.startsWith("https://nico.ms/")) {
      iframeElement = document.createElement("iframe");
      iframeElement.src = `https://embed.nicovideo.jp/watch/${
        jsonData.song.link.split("/")[3]
      }`;

      iframeElement.setAttribute("allowfullscreen", "allowfullscreen");
      iframeElement.setAttribute("allow", "autoplay");
      iframeElement.setAttribute("frameborder", "0");

      const videoContainer = document.querySelector(".videoContainer");
      videoContainer.style.display = null;

      videoContainer.append(iframeElement);
    }

    progressBar.value = 100;
    progressBar.textContent = `100%`;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const answerButtons = document.querySelectorAll(".answerButton");
  answerButtons.forEach((element) => {
    element.addEventListener("click", async () => {
      answerButtons.forEach((element) => {
        element.classList.add("is-loading");
        element.disabled = true;
      });

      try {
        await answer(element.getAttribute("data-answer"));
      } finally {
        answerButtons.forEach((element) => {
          element.classList.remove("is-loading");
          element.disabled = false;
        });
      }
    });
  });
});

// NND iframe

window.addEventListener("message", (event) => {
  if (event.data.eventName === "enterProgrammaticFullScreen") {
    exitFullScreen || (exitFullScreen = programmaticFullScreen(iframeElement));
  } else if (event.data.eventName === "exitProgrammaticFullScreen") {
    exitFullScreen && exitFullScreen();
    exitFullScreen = null;
  }
});
