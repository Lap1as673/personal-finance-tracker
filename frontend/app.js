const API_URL = 'http://localhost:8000/api/v1';

// Загрузка транзакций
async function loadTransactions() {
    try {
        const response = await fetch(`${API_URL}/transactions/`);
        const transactions = await response.json();
        
        const list = document.getElementById('transactions-list');
        list.innerHTML = '';

        if (transactions.length === 0) {
            list.innerHTML = '<p>Нет транзакций</p>';
            return;
        }

        transactions.forEach(transaction => {
            const div = document.createElement('div');
            div.className = `transaction-item transaction-${transaction.type}`;
            div.innerHTML = `
                <strong>${transaction.description}</strong>
                <span class="amount ${transaction.type}">
                    ${transaction.type === 'income' ? '+' : '-'}$${Math.abs(transaction.amount)}
                </span>
                <br>
                <small>${new Date(transaction.created_at).toLocaleDateString()}</small>
            `;
            list.appendChild(div);
        });
    } catch (error) {
        console.error('Ошибка загрузки транзакций:', error);
        document.getElementById('transactions-list').innerHTML = '<p>Ошибка загрузки</p>';
    }
}

// Добавление транзакции
document.getElementById('transaction-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = {
        description: document.getElementById('description').value,
        amount: parseFloat(document.getElementById('amount').value),
        type: document.getElementById('type').value
    };

    try {
        const response = await fetch(`${API_URL}/transactions/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        if (response.ok) {
            // Очищаем форму и обновляем список
            document.getElementById('transaction-form').reset();
            loadTransactions();
        }
    } catch (error) {
        console.error('Ошибка добавления транзакции:', error);
        alert('Ошибка добавления транзакции');
    }
});

// Загружаем транзакции при старте
loadTransactions();
