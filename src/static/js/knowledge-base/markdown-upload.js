document.addEventListener("DOMContentLoaded", function () {
  const fileInput = document.getElementById("id_file");
  const fileUploadLabel = document.querySelector(".file-upload");

  // Handle file drop
  fileUploadLabel.addEventListener("drop", (e) => {
    e.preventDefault();
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      fileInput.files = files; // Assign dropped files to the file input
      fileUploadLabel.textContent = files[0].name; // Update label text with file name
    }
  });
});
