// XON_MOTO JavaScript Utilities

document.addEventListener('DOMContentLoaded', function () {
    // 1. Mobile Menu Toggle
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const mobileMenu = document.getElementById('mobileMenu');
    if (mobileMenuBtn && mobileMenu) {
        mobileMenuBtn.addEventListener('click', function () {
            mobileMenu.classList.toggle('hidden');
        });
    }

    // 2. Alert auto-hide
    const alerts = document.querySelectorAll('.alert-box');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.style.transition = 'opacity 0.5s ease';
            alert.style.opacity = '0';
            setTimeout(function () {
                alert.remove();
            }, 500);
        }, 5000);
    });

    // 3. Image file preview for Add Listing Form
    const imageFileInput = document.getElementById('imageFileInput');
    const imagePreviewContainer = document.getElementById('imagePreviewContainer');
    const imagePreview = document.getElementById('imagePreview');

    if (imageFileInput && imagePreview && imagePreviewContainer) {
        imageFileInput.addEventListener('change', function (e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (event) {
                    imagePreview.src = event.target.result;
                    imagePreviewContainer.classList.remove('hidden');
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // 4. Live Credit Calculator on pages that have it
    initCreditCalculator();

    // 5. Inquiry Form via AJAX
    const inquiryForm = document.getElementById('inquiryForm');
    if (inquiryForm) {
        inquiryForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const submitBtn = inquiryForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Yuborilmoqda...';

            const formData = new FormData(inquiryForm);
            const data = {};
            formData.forEach((value, key) => data[key] = value);

            fetch('/api/inquiry', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
            .then(res => res.json())
            .then(response => {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
                const statusDiv = document.getElementById('inquiryStatus');
                if (statusDiv) {
                    statusDiv.classList.remove('hidden');
                    if (response.success) {
                        statusDiv.className = 'mt-4 p-4 rounded-xl bg-emerald-500/20 border border-emerald-500 text-emerald-300 text-sm';
                        statusDiv.innerHTML = '<i class="fas fa-check-circle mr-2"></i> ' + response.message;
                        inquiryForm.reset();
                    } else {
                        statusDiv.className = 'mt-4 p-4 rounded-xl bg-red-500/20 border border-red-500 text-red-300 text-sm';
                        statusDiv.innerHTML = '<i class="fas fa-exclamation-circle mr-2"></i> ' + (response.message || 'Xatolik yuz berdi');
                    }
                }
            })
            .catch(err => {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
                alert("Server bilan bog'lanishda xatolik yuz berdi.");
            });
        });
    }
});

// Avtokredit hisoblagich funksiyasi
function initCreditCalculator() {
    const calcPrice = document.getElementById('calcPrice');
    const calcInitialPercent = document.getElementById('calcInitialPercent');
    const calcTermMonths = document.getElementById('calcTermMonths');
    const calcInterestRate = document.getElementById('calcInterestRate');

    // Natijalar ko'rsatkichlari
    const resInitialSum = document.getElementById('resInitialSum');
    const resCreditSum = document.getElementById('resCreditSum');
    const resMonthlyPayment = document.getElementById('resMonthlyPayment');
    const resTotalPayment = document.getElementById('resTotalPayment');
    const resOverpayment = document.getElementById('resOverpayment');

    if (!calcPrice || !calcInitialPercent || !calcTermMonths || !calcInterestRate) return;

    function formatNumber(num) {
        return Math.round(num).toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
    }

    function calculate() {
        const price = parseFloat(calcPrice.value) || 0;
        const initialPercent = parseFloat(calcInitialPercent.value) || 0;
        const months = parseInt(calcTermMonths.value) || 12;
        const annualRate = parseFloat(calcInterestRate.value) || 0;

        const initialAmount = price * (initialPercent / 100);
        const loanAmount = Math.max(0, price - initialAmount);

        let monthlyPayment = 0;
        let totalPayment = 0;
        let overpayment = 0;

        if (loanAmount > 0 && months > 0) {
            const monthlyRate = (annualRate / 100) / 12;
            if (monthlyRate > 0) {
                // Annuitet to'lov formulasi
                monthlyPayment = loanAmount * (monthlyRate * Math.pow(1 + monthlyRate, months)) / (Math.pow(1 + monthlyRate, months) - 1);
            } else {
                monthlyPayment = loanAmount / months;
            }
            totalPayment = initialAmount + (monthlyPayment * months);
            overpayment = (monthlyPayment * months) - loanAmount;
        } else {
            totalPayment = price;
        }

        if (resInitialSum) resInitialSum.textContent = '$' + formatNumber(initialAmount);
        if (resCreditSum) resCreditSum.textContent = '$' + formatNumber(loanAmount);
        if (resMonthlyPayment) resMonthlyPayment.textContent = '$' + formatNumber(monthlyPayment);
        if (resTotalPayment) resTotalPayment.textContent = '$' + formatNumber(totalPayment);
        if (resOverpayment) resOverpayment.textContent = '$' + formatNumber(overpayment);

        // Foiz matnini yangilash
        const initialPercentLabel = document.getElementById('initialPercentLabel');
        if (initialPercentLabel) initialPercentLabel.textContent = initialPercent + '%';
    }

    calcPrice.addEventListener('input', calculate);
    calcInitialPercent.addEventListener('input', calculate);
    calcTermMonths.addEventListener('change', calculate);
    calcInterestRate.addEventListener('input', calculate);

    // Dastlabki hisoblash
    calculate();
}
