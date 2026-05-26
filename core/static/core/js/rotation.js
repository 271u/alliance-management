"use strict";
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
            id: row.dataset.id ?? "",
            name: row.dataset.name ?? "",
            rank: row.dataset.rank ?? "",
            position: indexElement ? Number(indexElement.textContent?.trim()) : -1,
        };
    });
    return conductors;
}
function getSelectedConductor() {
    const select = document.querySelector("#conductor-select");
    if (!select) {
        return null;
    }
    const selectedOption = select.selectedOptions[0];
    if (!selectedOption) {
        return null;
    }
    return {
        id: selectedOption.value,
        name: selectedOption.textContent?.trim() ?? "",
        rank: selectedOption.dataset.rank ?? "",
        position: 0
    };
}
