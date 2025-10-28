document.addEventListener("DOMContentLoaded", function () {
    const deleteModal = document.getElementById("deleteModal");
    const deleteForm = document.getElementById("deleteModalForm");
    const deleteBody = document.getElementById("deleteModalBody");

    deleteModal.addEventListener("show.bs.modal", function (event) {
        const button = event.relatedTarget;
        const userId = button.getAttribute("data-user-id");
        const fullName = button.getAttribute("data-user-fullname");

        deleteBody.textContent = `Вы уверены, что хотите удалить пользователя ${fullName.trim()}?`;

        deleteForm.action = `users/${userId}/delete`;
    });
});
