"use strict";
document.addEventListener("DOMContentLoaded", () => {
    initDragAndDrop();
    initDeleteButtons();
    updateRotationOrderInput();
});
function setButtonState(enabled) {
    const discardButton = document.getElementById("button-discard");
    const saveButton = document.getElementById("button-save");
    if (!discardButton || !saveButton) {
        console.warn("Save or discard button not found.");
        return;
    }
    discardButton.disabled = !enabled;
    saveButton.disabled = !enabled;
}
function getCurrentConductors() {
    const conductorRows = document.querySelectorAll(".rotation-row[data-id]");
    const conductors = Array.from(conductorRows).map((row) => {
        const indexElement = row.querySelector(".rotation-index");
        return {
            id: Number(row.dataset.id) ?? 0,
            name: row.dataset.name ?? "",
            rank: row.dataset.rank ?? "",
            position: indexElement ? Number(indexElement.textContent?.trim()) : -1,
        };
    });
    return conductors;
}
function initDragAndDrop() {
    const rotationList = document.getElementById("rotation-list");
    if (!rotationList) {
        return;
    }
    Sortable.create(rotationList, {
        animation: 150,
        handle: ".drag-handle",
        draggable: ".rotation-row",
        ghostClass: "rotation-row-ghost",
        chosenClass: "rotation-row-chosen",
        onEnd: () => {
            updateRotationOrderInput();
            setButtonState(true);
        },
    });
}
// obsolete?
function updateRotationOrderInput() {
    const orderInput = document.getElementById("rotation-order-input");
    if (!orderInput) {
        return;
    }
    const ids = Array.from(document.querySelectorAll("#rotation-list .rotation-row"))
        .map((row) => row.dataset.id)
        .filter((id) => id !== undefined);
    orderInput.value = ids.join(",");
}
function getCsrfToken() {
    const csrfInput = document.querySelector("input[name='csrfmiddlewaretoken']");
    return csrfInput?.value ?? "";
}
// obsolete?
function updateRotationIndexes() {
    const rows = document.querySelectorAll("#rotation-list .rotation-row[data-id]");
    rows.forEach((row, index) => {
        const indexElement = row.querySelector(".rotation-index");
        if (indexElement) {
            indexElement.textContent = String(index + 1);
        }
        row.dataset.position = String(index + 1);
    });
}
function initDeleteButtons() {
    const deleteButtons = document.querySelectorAll(".rotation-remove-button");
    deleteButtons.forEach((button) => {
        button.addEventListener("click", async () => {
            const row = button.closest(".rotation-row[data-id]");
            if (!row) {
                return;
            }
            const playerId = row.dataset.id;
            if (!playerId) {
                return;
            }
            const response = await fetch("/api/rotation/delete", {
                method: "DELETE",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCsrfToken(),
                },
                body: JSON.stringify({
                    id: playerId,
                }),
            });
            if (!response.ok) {
                console.error("Failed to delete rotation entry.");
                return;
            }
            window.location.reload();
        });
    });
}
function buttonDiscardAction() {
    setButtonState(false);
    window.location.reload();
}
async function buttonSaveAction() {
    const saveButton = document.getElementById("button-save");
    if (!saveButton) {
        console.warn("Save button not found.");
        return;
    }
    saveButton.classList.add("is-loading");
    const currentConductors = getCurrentConductors();
    let updateBody = [];
    let index = 1;
    currentConductors.forEach(element => {
        updateBody.push({
            id: element.id,
            position: index
        });
        index++;
    });
    const response = await fetch("/api/rotation/update", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCsrfToken(),
        },
        body: JSON.stringify(updateBody),
    });
    if (!response.ok) {
        console.error("Failed to update rotation.");
        return;
    }
    window.location.reload();
}
