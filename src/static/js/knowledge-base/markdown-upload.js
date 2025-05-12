document.addEventListener("DOMContentLoaded", function () {
  const fileInput = document.getElementById("id_file");
  const fileUploadLabel = document.querySelector(".file-upload");
  const fileNameArea = document.querySelector(".current-file");

  // Prevent Chrome/browser from trying to open the file
  fileUploadLabel.addEventListener("dragover", (e) => e.preventDefault());

  // Handle file drop
  fileUploadLabel.addEventListener("drop", (e) => {
    console.log("here");
    e.preventDefault();
    e.stopPropagation();
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      fileInput.files = files; // Assign dropped files to the file input
      fileNameArea.textContent = `Selected "${files[0].name}"`; // Update label text with file name
      console.log("here");
    }
  });

  // handle file uploaded via click
  fileInput.addEventListener("change", (e) => {
    fileNameArea.textContent = `Selected ${e.target.files[0].name}`;
  });
});
