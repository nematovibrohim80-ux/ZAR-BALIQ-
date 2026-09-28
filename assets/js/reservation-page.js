/**
 * AERO-SUSHI RESERVATION ENGINE (UZBEK)
 * Kapsulalarni tanlash, chipta xulosasi va kvant bortga chiqish chiptasi
 */

let selectedPod = 'nebula';
let selectedGrav = '0.05G (Sof Mikro-G)';

const POD_INFO = {
  nebula: {
    name: 'Nebula Pod (Shinam 2 kishilik)',
    capacity: '1 - 2 Sayohatchi',
    altitude: '88-qavat Sharqiy Terrasa',
    baseDeposit: '$50.00 / kishi',
    desc: 'Yumshoq ko‘k yulduz nuri va shaxsiy akustik muallaq stolga ega juftlik magnit kapsulasi.'
  },
  starlight: {
    name: 'Starlight Zali (Panoramali)',
    capacity: '3 - 6 Sayohatchi',
    altitude: '88-qavat Osmon Halqasi',
    baseDeposit: '$65.00 / kishi',
    desc: '360° golografik galaktika gumbazi, mustaqil orbital aylanish tezligi va audio izolyatsiyasi.'
  },
  commander: {
    name: "Qo‘mondonlik VIP Sferasi",
    capacity: '6 - 10 Sayohatchi',
    altitude: 'Apex Orbital Zali',
    baseDeposit: '$100.00 / kishi',
    desc: 'Shaxsiy Itamae oshpazi, eksklyuziv 18 xil taomli mikro-gravitatsion omakase va shampan bug‘i.'
  }
};

function selectPod(podKey) {
  audioFX.soundClick();
  selectedPod = podKey;

  document.querySelectorAll('.pod-select-card').forEach(card => {
    card.classList.remove('border-cyan-400', 'box-glow-cyan', 'bg-cyan-950/20');
    card.classList.add('border-slate-800');
  });

  const activeCard = document.getElementById(`pod-card-${podKey}`);
  if (activeCard) {
    activeCard.classList.add('border-cyan-400', 'box-glow-cyan', 'bg-cyan-950/20');
    activeCard.classList.remove('border-slate-800');
  }

  const podInput = document.getElementById('selected-pod-input');
  if (podInput) podInput.value = podKey;

  updateReservationSummary();
}

function handleGravChange(val) {
  const labels = {
    '0': '0.05G (Sof Mikro-G Vaznsizlik)',
    '1': '0.16G (Oy Tortishish Kuchi)',
    '2': '0.38G (Mars Tortishish Kuchi)',
    '3': '1.00G (Yer Standart Gravitatsiyasi)'
  };
  selectedGrav = labels[val] || '0.12G';
  const labelEl = document.getElementById('grav-slider-label');
  if (labelEl) labelEl.textContent = selectedGrav;
  updateReservationSummary();
}

function updateReservationSummary() {
  const pod = POD_INFO[selectedPod] || POD_INFO.nebula;
  const nameInput = document.getElementById('res-name');
  const guestsInput = document.getElementById('res-guests');
  const dateInput = document.getElementById('res-date');
  const timeInput = document.getElementById('res-time');

  const summaryPodName = document.getElementById('summary-pod-name');
  const summaryGuests = document.getElementById('summary-guests');
  const summaryDateTime = document.getElementById('summary-datetime');
  const summaryGrav = document.getElementById('summary-grav');

  if (summaryPodName) summaryPodName.textContent = pod.name;
  if (summaryGuests) summaryGuests.textContent = `${guestsInput ? guestsInput.value : 2} Sayohatchi`;
  
  const dateVal = dateInput && dateInput.value ? dateInput.value : '2088-10-12';
  const timeVal = timeInput && timeInput.value ? timeInput.value : '19:30 Parvozi';
  if (summaryDateTime) summaryDateTime.textContent = `${dateVal} @ ${timeVal}`;
  if (summaryGrav) summaryGrav.textContent = selectedGrav;
}

function handleReservationSubmit(e) {
  e.preventDefault();
  audioFX.soundSuccess();

  const nameVal = document.getElementById('res-name').value || 'Qo‘mondon Mehmon';
  const guestsVal = document.getElementById('res-guests').value || '2';
  const dateVal = document.getElementById('res-date').value || '2088-10-14';
  const timeVal = document.getElementById('res-time').value || '19:30 Orbital Smena';
  const pod = POD_INFO[selectedPod];

  const passId = 'AG-TKT-' + Math.floor(100000 + Math.random() * 900000);
  document.getElementById('pass-ticket-id').textContent = passId;
  document.getElementById('pass-guest-name').textContent = nameVal.toUpperCase();
  document.getElementById('pass-pod-name').textContent = pod.name;
  document.getElementById('pass-guests').textContent = `${guestsVal} Sayohatchi`;
  document.getElementById('pass-shift').textContent = `${dateVal} | ${timeVal}`;
  document.getElementById('pass-grav').textContent = selectedGrav;

  const modal = document.getElementById('reservation-success-modal');
  if (modal) modal.classList.remove('hidden');

  showToast('Bron Tasdiqlandi', `${nameVal} uchun ${passId} raqamli chipta rasmiylashtirildi.`, 'sushi');
}

function closeReservationModal() {
  audioFX.soundClick();
  const modal = document.getElementById('reservation-success-modal');
  if (modal) modal.classList.add('hidden');
}

function downloadTicketPass() {
  audioFX.soundClick();
  showToast('Chipta Saqlandi', 'Kvant chiptasi kiber-terminal keshiga yuklab olindi.', 'cyan');
}

document.addEventListener('DOMContentLoaded', () => {
  const dateInput = document.getElementById('res-date');
  if (dateInput) {
    const today = new Date().toISOString().split('T')[0];
    dateInput.min = today;
    dateInput.value = today;
  }
  updateReservationSummary();
});
