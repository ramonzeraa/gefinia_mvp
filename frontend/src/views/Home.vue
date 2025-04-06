<template>
  <div class="dashboard-container">
    <Navbar />
    <h1>Dashboard do GeFinIA</h1>
    <p>Olá, {{ user?.name || 'Usuário' }}! Aqui está o resumo das suas finanças.</p>

    <!-- Resumo financeiro -->
    <div class="summary">
      <h2>Resumo do Mês Atual</h2>
      <div class="summary-cards">
        <div class="card">
          <h3>Total de Ganhos</h3>
          <p>R$ {{ summary.totalGains != null ? summary.totalGains.toFixed(2) : '0.00' }}</p>
        </div>
        <div class="card">
          <h3>Total de Despesas</h3>
          <p>R$ {{ summary.totalExpenses != null ? summary.totalExpenses.toFixed(2) : '0.00' }}</p>
        </div>
        <div class="card">
          <h3>Score Financeiro</h3>
          <p>{{ summary.financialScore != null ? summary.financialScore.toFixed(2) : 'N/A' }}</p>
        </div>
      </div>
    </div>

    <!-- Últimos ganhos -->
    <div class="recent-transactions">
      <h2>Últimos Ganhos</h2>
      <div v-if="recentGains && recentGains.length">
        <ul>
          <li v-for="gain in recentGains" :key="gain.id">
            {{ gain.description || 'Sem descrição' }} - R$ 
            {{ gain.amount != null ? gain.amount.toFixed(2) : '0.00' }} 
            ({{ gain.gain_date ? new Date(gain.gain_date).toLocaleDateString() : 'N/A' }})
          </li>
        </ul>
      </div>
      <p v-else>Nenhum ganho recente.</p>
    </div>

    <!-- Últimas despesas -->
    <div class="recent-transactions">
      <h2>Últimas Despesas</h2>
      <div v-if="recentExpenses && recentExpenses.length">
        <ul>
          <li v-for="expense in recentExpenses" :key="expense.id">
            {{ expense.description || 'Sem descrição' }} - R$ 
            {{ expense.amount != null ? expense.amount.toFixed(2) : '0.00' }} 
            ({{ expense.expense_date ? new Date(expense.expense_date).toLocaleDateString() : 'N/A' }})
          </li>
        </ul>
      </div>
      <p v-else>Nenhuma despesa recente.</p>
    </div>

    <router-link :to="'/profile/' + user?.id" class="btn">Ver Perfil Completo</router-link>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      user: null,
      summary: {
        totalGains: 0,
        totalExpenses: 0,
        financialScore: null
      },
      recentGains: [],
      recentExpenses: []
    };
  },
  mounted() {
    this.loadUserData();
    this.loadSummary();
    this.loadRecentTransactions();
  },
  methods: {
    getHeaders() {
      const token = localStorage.getItem('token');
      return {
        Authorization: `Bearer ${token}`
      };
    },
    loadUserData() {
      const userData = localStorage.getItem('user');
      if (userData) {
        this.user = JSON.parse(userData);
      }
    },
    async loadSummary() {
      try {
        const userId = this.user?.id;
        const response = await axios.get(`http://localhost:5000/api/financial-score/${userId}`, {
          headers: this.getHeaders()
        });
        const data = response.data[0] || {};
        this.summary = {
          totalGains: data.total_gains || 0,
          totalExpenses: data.total_expenses || 0,
          financialScore: data.financial_score || null
        };
      } catch (error) {
        console.error('Erro ao carregar resumo financeiro:', error);
      }
    },
    async loadRecentTransactions() {
      try {
        const userId = this.user?.id;
        // Carregar últimos ganhos
        const gainsResponse = await axios.get(`http://localhost:5000/api/gains/${userId}`, {
          headers: this.getHeaders()
        });
        this.recentGains = (gainsResponse.data || []).slice(0, 5);

        // Carregar últimas despesas
        const expensesResponse = await axios.get(`http://localhost:5000/api/expenses/${userId}`, {
          headers: this.getHeaders()
        });
        this.recentExpenses = (expensesResponse.data || []).slice(0, 5);
      } catch (error) {
        console.error('Erro ao carregar transações recentes:', error);
        this.recentGains = [];
        this.recentExpenses = [];
      }
    }
  }
};
</script>

<style scoped>
.dashboard-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

h1, h2 {
  color: #2c3e50;
  margin-bottom: 20px;
}

p {
  color: #34495e;
  font-size: 16px;
  margin: 10px 0;
}

.summary {
  margin-bottom: 40px;
}

.summary-cards {
  display: flex;
  gap: 20px;
  justify-content: center;
}

.card {
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  text-align: center;
  flex: 1;
}

.card h3 {
  color: #2c3e50;
  margin-bottom: 10px;
}

.card p {
  font-size: 18px;
  color: #34495e;
}

.recent-transactions {
  margin-bottom: 40px;
}

ul {
  list-style: none;
  padding: 0;
}

li {
  padding: 10px;
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 5px;
  margin-bottom: 10px;
}

.btn {
  display: inline-block;
  background-color: #3498db;
  color: white;
  padding: 10px 20px;
  text-decoration: none;
  border-radius: 5px;
  transition: background-color 0.3s;
}

.btn:hover {
  background-color: #2980b9;
}
</style>