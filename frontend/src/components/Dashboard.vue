<template>
  <navbar />
  <div class="dashboard-container">
    <h1>Dashboard do GeFinIA</h1>
    <p>Olá, {{ user?.name || 'Usuário' }}! Aqui está o resumo das suas finanças.</p>

    <div class="filter">
      <h3>Filtrar por Período</h3>
      <div class="filter-controls">
        <select v-model="selectedMonth">
          <option v-for="month in months" :key="month.value" :value="month.value">
            {{ month.name }}
          </option>
        </select>
        <select v-model="selectedYear">
          <option v-for="year in years" :key="year" :value="year">
            {{ year }}
          </option>
        </select>
        <button @click="applyFilter">Aplicar Filtro</button>
      </div>
      <p>Período Selecionado: {{ selectedMonthName }}/{{ selectedYear }}</p>
    </div>

    <!-- Resumo financeiro -->
    <div class="summary">
      <h2>Resumo do Período</h2>
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
          <p>{{ summary.financialScore != null ? summary.financialScore.toFixed(2) : 'Não identificado' }}</p>
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
            ({{ gain.date ? new Date(gain.date).toLocaleDateString() : 'N/A' }})
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
            ({{ expense.date ? new Date(expense.date).toLocaleDateString() : 'N/A' }})
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
      recentExpenses: [],
      selectedMonth: null,
      selectedYear: null,
      months: [
        { name: 'Janeiro', value: 1 },
        { name: 'Fevereiro', value: 2 },
        { name: 'Março', value: 3 },
        { name: 'Abril', value: 4 },
        { name: 'Maio', value: 5 },
        { name: 'Junho', value: 6 },
        { name: 'Julho', value: 7 },
        { name: 'Agosto', value: 8 },
        { name: 'Setembro', value: 9 },
        { name: 'Outubro', value: 10 },
        { name: 'Novembro', value: 11 },
        { name: 'Dezembro', value: 12 }
      ],
      years: []
    };
  },
  computed: {
    selectedMonthName() {
      const month = this.months.find(m => m.value === this.selectedMonth);
      return month ? month.name : 'Selecione um mês';
    }
  },
  mounted() {
    this.loadUserData();
    this.initializeFilters();
    this.loadSummary();
  },
  methods: {
    getHeaders() {
      const token = localStorage.getItem('token');
      console.log('Enviando token no cabeçalho:', token);
      return token ? { Authorization: token } : {};
    },
    loadUserData() {
      const userData = localStorage.getItem('user');
      if (userData) {
        this.user = JSON.parse(userData);
      }
    },
    initializeFilters() {
      // mes e ano atuais como padrão
      const now = new Date();
      this.selectedMonth = now.getMonth() + 1; // Janeiro é 0, retorna de 0-11
      this.selectedYear = now.getFullYear();

      // Preencher anos de 5 anos atrás e 5 anos à frente do ano atual
      // por exeemplo: o ano atual é 2025, os anos serão de 2020 a 2030
      const currentYear = now.getFullYear();
      this.years = Array.from({ length: 11 }, (_, i) => currentYear - 5 + i);
    },
    async loadSummary() {
      try {
        const userId = this.user?.id;
        console.log('User ID da rota:', userId);
        if (!userId) {
          console.error('User ID não encontrado.');
          return;
        }

        const params = {
          month: this.selectedMonth,
          year: this.selectedYear
        };
        console.log('Parâmetros para resumo financeiro:', params);

        const response = await axios.get(`http://localhost:5000/api/financial-score/${userId}`, {
          headers: this.getHeaders(),
          params
        });
        const data = response.data || {};
        this.summary = {
          totalGains: data.total_gains || 0,
          totalExpenses: data.total_expenses || 0,
          financialScore: data.financial_score || null
        };
 
        // Carregar últimos ganhos
        const gainsResponse = await axios.get(`http://localhost:5000/api/gains/${this.user.id}`, {
          headers: this.getHeaders(),
          params
        });
        this.recentGains = (gainsResponse.data || []).slice(0, 5);

        // Carregar últimas despesas
        const expensesResponse = await axios.get(`http://localhost:5000/api/expenses/${this.user.id}`, {
          headers: this.getHeaders(),
          params
        });
        this.recentExpenses = (expensesResponse.data || []).slice(0, 5);
      } catch (error) {
        console.error('Erro ao carregar dados:', error);
        this.summary = {totalGains: 0, totalExpenses: 0, financialScore: null };
        this.recentGains = [];
        this.recentExpenses = [];
      }
    },
    applyFilter() {
      this.loadSummary();
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

.filter {
  margin-bottom: 20px;
}

.filter-controls {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-bottom: 10px;
}

select, button {
  padding: 8px;
  border-radius: 4px;
  border: 1px solid #ddd;
}

button {
  background-color: #3498db;
  color: white;
  border: none;
  cursor: pointer;
}

button:hover {
  background-color: #2980b9;
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