document.addEventListener("DOMContentLoaded", () => {
  const selector = document.querySelector(".contactType");

  selector.addEventListener("change", (e) => {
    document.querySelectorAll(".mchoice").forEach((element) => {
      element.style.display = "none";

      element.querySelectorAll("input, textarea, select").forEach((input) => {
        input.required = false;
      });
    });

    const id = e.target.value;
    console.log(id);

    const target = document.querySelector(`.${id}`);
    if (target) {
      target.style.display = "block";

      target.querySelectorAll("input, textarea, select").forEach((input) => {
        input.required = true;
      });
    }
  });
});

function enableSubmit() {
  document.getElementById("submit-button").disabled = false;
}
