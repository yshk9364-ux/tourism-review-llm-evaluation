const cases = [
  { id: 'R008', label: '反讽表达', review: '真贴心，排队一个半小时还不让坐，太阳晒得我很开心。', gold: '负面｜排队;服务｜需复核：是', v1: '正面｜排队｜需复核：否', v2: '负面｜排队;服务｜需复核：是', error: '情感误判、问题漏标、复核判断错误', note: 'V1 按“真贴心”和“很开心”的字面意思判断；V2 加入反讽规则后，结合排队与暴晒事实识别实际不满。' },
  { id: 'R010', label: '正负混合', review: '儿童区玩具旧了一些，但工作人员会主动帮忙，孩子玩得还行。', gold: '中性｜设施;服务｜需复核：是', v1: '正面｜服务｜需复核：否', v2: '中性｜设施;服务｜需复核：是', error: '情感误判、问题漏标、复核判断错误', note: 'V2 明确保留正负两类信息：设施陈旧与服务主动并存，因此整体判断为中性。' },
  { id: 'R009', label: '多问题评论', review: '宣传页说玻璃栈道开放，到了才知道在维修。', gold: '负面｜宣传;设施｜需复核：否', v1: '负面｜宣传｜需复核：否', v2: '负面｜宣传;设施｜需复核：否', error: '问题漏标', note: 'V1 只识别宣传信息不符，遗漏“在维修”所体现的设施状态；V2 按多标签规则保留两个独立主题。' },
  { id: 'R033', label: '信息不足', review: '朋友说这里很好玩，但我自己还没去过。', gold: '中性｜其他｜需复核：是', v1: '正面｜无明显问题｜需复核：否', v2: '中性｜其他｜需复核：是', error: '情感误判、问题多标、复核判断错误', note: '原文是二手转述，不应直接视为第一手正面体验；V2 将此类信息不足场景纳入复核规则。' },
  { id: 'R007', label: '证据覆盖', review: '洗手间有两个水龙头坏了，地面还有积水。', gold: '负面｜设施;卫生｜需复核：否', v1: '负面｜设施｜需复核：否', v2: '负面｜设施;卫生｜需复核：否', error: '问题漏标；证据覆盖不完整', note: 'V1 证据只聚焦“水龙头坏了”，没有覆盖“地面还有积水”对应的卫生问题；V2 的证据约束支持更完整地保留原文信息。' }
];

const picker = document.querySelector('#casePicker');
const detail = document.querySelector('#caseDetail');

function renderCase(index) {
  const item = cases[index];
  if (!item || !picker || !detail) return;

  picker.querySelectorAll('button').forEach((button, buttonIndex) => {
    button.classList.toggle('active', buttonIndex === index);
    button.setAttribute('aria-pressed', String(buttonIndex === index));
  });

  detail.innerHTML = `
    <div class="case-meta"><span>${item.id}</span><b>${item.label}</b></div>
    <blockquote>“${item.review}”</blockquote>
    <div class="case-result-list">
      <div><span>基准标签</span><strong>${item.gold}</strong><p>本次对比使用的参考结果</p></div>
      <div><span>Prompt V1</span><strong>${item.v1}</strong><p>错误类型：${item.error}</p></div>
      <div class="v2-result"><span>Prompt V2</span><strong>${item.v2}</strong><p>规则增强后的结构化结果</p></div>
    </div>
    <p class="case-note"><b>优化说明</b>${item.note}</p>`;
}

if (picker && detail) {
  cases.forEach((item, index) => {
    const button = document.createElement('button');
    button.type = 'button';
    button.innerHTML = `<span>${String(index + 1).padStart(2, '0')}</span><b>${item.label}</b><em>${item.id}</em>`;
    button.addEventListener('click', () => renderCase(index));
    picker.appendChild(button);
  });
  renderCase(0);
}

const header = document.querySelector('.site-header');
const menuToggle = document.querySelector('.menu-toggle');
const nav = document.querySelector('.main-nav');

if (header) {
  const updateHeader = () => header.classList.toggle('scrolled', window.scrollY > 24);
  updateHeader();
  window.addEventListener('scroll', updateHeader, { passive: true });
}

if (menuToggle && nav) {
  menuToggle.addEventListener('click', () => {
    const isOpen = nav.classList.toggle('open');
    menuToggle.setAttribute('aria-expanded', String(isOpen));
    document.body.classList.toggle('menu-open', isOpen);
  });

  nav.querySelectorAll('a').forEach((link) => link.addEventListener('click', () => {
    nav.classList.remove('open');
    menuToggle.setAttribute('aria-expanded', 'false');
    document.body.classList.remove('menu-open');
  }));
}

if ('IntersectionObserver' in window) {
  const revealItems = document.querySelectorAll('.reveal');
  document.documentElement.classList.add('reveal-ready');
  const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('shown');
        revealObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });
  revealItems.forEach((item) => revealObserver.observe(item));
}
