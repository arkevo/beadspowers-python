const API = "/tasks";
let tasks = [];
let activeFilter = "all";
let activeEditId = null; // tracks which task row is in edit mode

// ---- Toast (error feedback) ----
let _toastTimer = null;
function showToast(message) {
  const toast = document.getElementById("toast");
  toast.textContent = message;
  toast.hidden = false;
  clearTimeout(_toastTimer);
  _toastTimer = setTimeout(() => { toast.hidden = true; }, 3000);
}

// ---- API helpers ----

async function fetchTasks() {
  const res = await fetch(API);
  tasks = await res.json();
  renderTasks();
}

async function apiCreateTask(title) {
  const res = await fetch(API, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title }),
  });
  if (!res.ok) throw new Error("Failed to create task");
  return res.json();
}

async function apiUpdateTask(id, patch) {
  const res = await fetch(`${API}/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(patch),
  });
  if (!res.ok) throw new Error("Failed to update task");
  return res.json();
}

async function apiDeleteTask(id) {
  const res = await fetch(`${API}/${id}`, { method: "DELETE" });
  if (!res.ok) throw new Error("Failed to delete task");
}

// ---- DOM helpers ----

function createButton(className, label, text) {
  const btn = document.createElement("button");
  btn.className = `btn btn-icon ${className}`;
  btn.setAttribute("aria-label", label);
  btn.setAttribute("title", label);
  btn.textContent = text;
  return btn;
}

// ---- Render ----

function filteredTasks() {
  if (activeFilter === "active") return tasks.filter((t) => !t.completed);
  if (activeFilter === "completed") return tasks.filter((t) => t.completed);
  return tasks;
}

function renderTasks() {
  const list = document.getElementById("task-list");
  const emptyState = document.getElementById("empty-state");
  const countEl = document.getElementById("task-count");

  const visible = filteredTasks();
  const activeCount = tasks.filter((t) => !t.completed).length;

  countEl.textContent = activeCount > 0 ? `${activeCount} left` : "";
  list.textContent = "";

  if (visible.length === 0) {
    emptyState.hidden = false;
    return;
  }
  emptyState.hidden = true;

  visible.forEach((task) => {
    const li = document.createElement("li");
    li.className = `task-row${task.completed ? " completed" : ""}`;
    li.dataset.id = task.id;

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.className = "task-checkbox";
    checkbox.checked = task.completed;
    checkbox.setAttribute("aria-label", task.completed ? "Mark incomplete" : "Mark complete");

    const span = document.createElement("span");
    span.className = "task-text";
    span.textContent = task.title;

    const actions = document.createElement("div");
    actions.className = "task-actions";
    actions.appendChild(createButton("btn-edit", "Edit task", "\u270F\uFE0F"));
    actions.appendChild(createButton("btn-delete", "Delete task", "\uD83D\uDDD1\uFE0F"));

    li.appendChild(checkbox);
    li.appendChild(span);
    li.appendChild(actions);
    list.appendChild(li);
  });
}

// ---- Add task ----

document.getElementById("add-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const input = document.getElementById("task-input");
  const title = input.value.trim();
  if (!title) return;
  input.disabled = true;
  try {
    const task = await apiCreateTask(title);
    tasks.push(task);
    input.value = "";
    document.getElementById("add-btn").disabled = true;
    renderTasks();
    input.focus();
  } catch (err) {
    showToast("Failed to add task — please try again.");
  } finally {
    input.disabled = false;
  }
});

document.getElementById("task-input").addEventListener("input", (e) => {
  document.getElementById("add-btn").disabled = !e.target.value.trim();
});

// ---- Task list delegation ----

document.getElementById("task-list").addEventListener("click", async (e) => {
  const row = e.target.closest(".task-row");
  if (!row) return;
  const id = row.dataset.id;

  if (e.target.matches(".task-checkbox")) {
    const completed = e.target.checked;
    try {
      const updated = await apiUpdateTask(id, { completed });
      const idx = tasks.findIndex((t) => t.id === id);
      if (idx !== -1) tasks[idx] = updated;
      renderTasks();
    } catch (err) {
      e.target.checked = !completed;
      showToast("Failed to update task — please try again.");
    }
    return;
  }

  if (e.target.closest(".btn-delete")) {
    try {
      await apiDeleteTask(id);
      tasks = tasks.filter((t) => t.id !== id);
      renderTasks();
    } catch (err) {
      showToast("Failed to delete task — please try again.");
    }
    return;
  }

  if (e.target.closest(".btn-edit")) {
    // auto-cancel existing edit mode before opening a new one
    if (activeEditId && activeEditId !== id) {
      renderTasks();
    }
    enterEditMode(row, id);
    return;
  }
});

function enterEditMode(row, id) {
  const task = tasks.find((t) => t.id === id);
  if (!task) return;
  activeEditId = id;

  const textSpan = row.querySelector(".task-text");
  const actions = row.querySelector(".task-actions");

  const input = document.createElement("input");
  input.type = "text";
  input.className = "task-edit-input";
  input.value = task.title;
  input.setAttribute("aria-label", "Edit task text");
  input.maxLength = 200;

  textSpan.replaceWith(input);

  actions.textContent = "";
  const saveBtn = createButton("btn-save", "Save task", "\u2705");
  const cancelBtn = createButton("btn-cancel", "Cancel edit", "\u274C");
  actions.appendChild(saveBtn);
  actions.appendChild(cancelBtn);

  input.focus();
  input.select();

  async function saveEdit() {
    const newTitle = input.value.trim();
    if (!newTitle) {
      input.focus();
      return;
    }
    saveBtn.disabled = true;
    try {
      const updated = await apiUpdateTask(id, { title: newTitle });
      const idx = tasks.findIndex((t) => t.id === id);
      if (idx !== -1) tasks[idx] = updated;
      activeEditId = null;
      renderTasks();
    } catch (err) {
      saveBtn.disabled = false;
      showToast("Failed to save edit — please try again.");
    }
  }

  function cancelEdit() {
    activeEditId = null;
    renderTasks();
  }

  saveBtn.addEventListener("click", saveEdit);
  cancelBtn.addEventListener("click", cancelEdit);
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter") saveEdit();
    if (e.key === "Escape") cancelEdit();
  });
}

// ---- Filter ----

document.querySelector(".filter-nav").addEventListener("click", (e) => {
  const btn = e.target.closest(".filter-btn");
  if (!btn) return;
  document.querySelectorAll(".filter-btn").forEach((b) => {
    b.classList.remove("active");
    b.setAttribute("aria-pressed", "false");
  });
  btn.classList.add("active");
  btn.setAttribute("aria-pressed", "true");
  activeFilter = btn.dataset.filter;
  renderTasks();
});

// ---- Init ----
fetchTasks();
