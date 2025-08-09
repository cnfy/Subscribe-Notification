document.addEventListener('DOMContentLoaded', () => {
  // 折叠侧边栏逻辑
  const sidebar = document.querySelector('.sidebar');
  const toggleBtn = document.querySelector('.toggle-btn');
    // 初始化状态
  if (localStorage.getItem('sidebarCollapsed') === 'true') {
    document.documentElement.classList.add('sidebar-collapsed');
  }

  // 切换状态
  toggleBtn.addEventListener('click', () => {
    const html = document.documentElement;
    const isCollapsed = html.classList.toggle('sidebar-collapsed');
    localStorage.setItem('sidebarCollapsed', isCollapsed);
  });

  // 页面加载完成后移除 no-animate
  document.documentElement.classList.remove('no-animate');

  // 创建任务弹窗逻辑
  const taskModal = document.getElementById("taskModal");
  const openCreateBtn = document.getElementById("openModal");
  const closeCreateBtn = document.getElementById("closeModal");

  if (openCreateBtn && closeCreateBtn && taskModal) {
    openCreateBtn.onclick = () => taskModal.style.display = "block";
    closeCreateBtn.onclick = () => taskModal.style.display = "none";
    window.addEventListener('click', (event) => {
      if (event.target === taskModal) {
        taskModal.style.display = "none";
      }
    });
  }

  // 修改任务弹窗逻辑
  const editModal = document.getElementById("editModal");
  const closeEditBtn = document.getElementById("closeEditModal");
  const editForm = document.getElementById("editForm");

  if (closeEditBtn && editModal) {
    closeEditBtn.onclick = () => editModal.style.display = "none";
    window.addEventListener('click', (event) => {
      if (event.target === editModal) {
        editModal.style.display = "none";
      }
    });
  }

  if (editForm) {
    editForm.onsubmit = function (e) {
      e.preventDefault();
      const taskId = document.getElementById("editTaskId").value;
      const formData = new FormData(editForm);

      fetch(`/edit/${taskId}`, {
        method: "POST",
        body: formData
      }).then(() => {
        editModal.style.display = "none";
        location.reload();
      });
    };
  }

  // 自动高亮当前导航链接
  const links = document.querySelectorAll('.nav a');
  const currentUrl = window.location.pathname;
  links.forEach(link => {
    if (link.getAttribute('href') === currentUrl) {
      link.classList.add('active');
    }
  });

  // 自定义 tooltip 逻辑
  const tooltip = document.createElement('div');
  tooltip.className = 'tooltip-box';
  document.body.appendChild(tooltip);

  document.querySelectorAll('.tooltip-target').forEach(el => {
    el.addEventListener('mouseenter', () => {
      const text = el.getAttribute('data-tooltip');
      if (text) {
        tooltip.textContent = text;
        tooltip.style.opacity = '1';
      }
    });

    el.addEventListener('mousemove', e => {
      tooltip.style.top = `${e.pageY + 12}px`;
      tooltip.style.left = `${e.pageX + 12}px`;
    });

    el.addEventListener('mouseleave', () => {
      tooltip.style.opacity = '0';
    });
  });
});

window.addEventListener("load", function () {
  const allElements = document.querySelectorAll("html.sidebar-collapsed *");
  allElements.forEach(el => el.style.transition = "");
});

function openEditModal(id, name, url, xpath, email) {
  const editModal = document.getElementById("editModal");

  // 设置表单字段值
  document.getElementById("editTaskId").value = id;
  document.getElementById("editName").value = name;
  document.getElementById("editUrl").value = url;
  document.getElementById("editXpath").value = xpath;
  document.getElementById("editEmail").value = email;

  // 显示弹窗
  editModal.style.display = "block";
}

// 任务详情弹窗逻辑
const detailModal = document.getElementById("detailModal");
const closeDetailBtn = document.getElementById("closeDetailModal");

if (detailModal && closeDetailBtn) {
  closeDetailBtn.onclick = () => detailModal.style.display = "none";
  window.addEventListener('click', (event) => {
    if (event.target === detailModal) {
      detailModal.style.display = "none";
    }
  });
}

// 点击任务卡片弹出详情
document.querySelectorAll(".task-card").forEach(card => {
  card.addEventListener("click", function (e) {
    // 排除创建卡片
    if (card.classList.contains("create-card")) return;

    // 避免点击按钮时触发弹窗
    if (e.target.closest(".card-actions")) return;

    document.getElementById("detailName").textContent = card.dataset.name;
    document.getElementById("detailUrl").textContent = card.dataset.url;
    document.getElementById("detailXpath").textContent = card.dataset.xpath;
    document.getElementById("detailEmail").textContent = card.dataset.email;
    document.getElementById("detailStatus").textContent = card.dataset.status;

    detailModal.style.display = "block";
  });
});
