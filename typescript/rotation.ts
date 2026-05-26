type Conductor = {
  id: string;
  name: string;
  rank: string;
  position: number;
};

function setButtonState(enabled: boolean): void {
  const discardButton = document.getElementById("button-discard") as HTMLButtonElement | null;
  const saveButton = document.getElementById("button-save") as HTMLButtonElement | null;

  if (!discardButton || !saveButton) {
    console.warn("Save or discard button not found.");
    return;
  }

  discardButton.disabled = !enabled;
  saveButton.disabled = !enabled;
}

function getCurrentConductors(): Conductor[] {
  const conductorRows = document.querySelectorAll<HTMLElement>(".rotation-row[data-id]");

  const conductors = Array.from(conductorRows).map((row): Conductor => {
    const indexElement = row.querySelector<HTMLElement>(".rotation-index");

    return {
      id: row.dataset.id ?? "",
      name: row.dataset.name ?? "",
      rank: row.dataset.rank ?? "",
      position: indexElement ? Number(indexElement.textContent?.trim()) : -1,
    };
  });
  return conductors;
}

function getSelectedConductor(): Conductor | null {
  const select = document.querySelector<HTMLSelectElement>("#conductor-select");

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
