<template>
  <navbar />
    <div class="profile-container">
      <h1>Perfil de {{ user.name }}</h1>
      <h2>Seu Score Financeiro: {{ financialScore.score.toFixed(2) }}%</h2>
      <p>Saldo: R${{ financialScore.saldo }}</p>
      <h3>Resumo financeiro:</h3>
      <p>Total de ganhos: R$ {{ totalGains.toFixed(2) }}</p>
      <p>Total de despesas: R$ {{ totalExpenses.toFixed(2) }}</p>
      <h3>Grafico de gastos (Mockup)</h3>
      <div style="width: 400px; height: 200px; margin: 0 auto;">
        <canvas ref="chart"></canvas>
      </div>

      <!-- Formulário para adicionar ganho -->
    <h3>Adicionar Ganho</h3>
    <form @submit.prevent="addGain">
      <input v-model="newGain.description" placeholder="Descrição" required />
      <input v-model.number="newGain.amount" type="number" step="0.01" placeholder="Valor" required />
      <input v-model="newGain.source" placeholder="Fonte" required />
      <input v-model="newGain.date" type="date" required />
      <button type="submit">Adicionar Ganho</button>
    </form>

    <h3>Meus Ganhos</h3>
    <ul>
      <li v-for="gain in gains" :key="gain.id">
        {{ gain.description }} - R${{ gain.amount.toFixed(2) }} ({{ gain.source }}, {{ gain.date }})
        <button @click="editGain(gain)">Editar</button>
        <button @click="deleteGain(gain.id)">Deletar</button>
      </li>
    </ul>

    <div v-if="editingGain" class="edit-form">
      <h3>Editar Ganho</h3>
      <form @submit.prevent="updateGain">
        <input v-model="editingGain.description" placeholder="Descrição" required />
        <input v-model.number="editingGain.amount" type="number" step="0.01" placeholder="Valor" required />
        <input v-model="editingGain.source" placeholder="Fonte" required />
        <input v-model="editingGain.date" type="date" required />
        <button type="submit">Salvar</button>
        <button @click="cancelEdit">Cancelar</button>
      </form>
    </div>

    <h3>Adicionar Despesa</h3>
    <form @submit.prevent="addExpense">
      <input v-model="newExpense.description" placeholder="Descrição" required />
      <input v-model.number="newExpense.amount" type="number" step="0.01" placeholder="Valor" required />
      <select v-model.number="newExpense.category_id" required>
        <option v-for="category in categories" :key="category.id" :value="category.id">
          {{ category.name }}
        </option>
      </select>
      <input v-model="newExpense.date" type="date" required />
      <button type="submit">Adicionar Despesa</button>
    </form>

    <h3>Minhas Despesas</h3>
    <ul>
      <li v-for="expense in expenses" :key="expense.id">
        {{ expense.description }} - R${{ expense.amount.toFixed(2) }} ({{ getCategoryName(expense.category_id) }}, {{ expense.date }})
        <button @click="editExpense(expense)">Editar</button>
        <button @click="deleteExpense(expense.id)">Deletar</button>
      </li>
    </ul>

    <div v-if="editingExpense" class="edit-form">
      <h3>Editar Despesa</h3>
      <form @submit.prevent="updateExpense">
        <input v-model="editingExpense.description" placeholder="Descrição" required />
        <input v-model.number="editingExpense.amount" type="number" step="0.01" placeholder="Valor" required />
        <select v-model.number="editingExpense.category_id" required>
          <option v-for="category in categories" :key="category.id" :value="category.id">
            {{ category.name }}
          </option>
        </select>
        <input v-model="editingExpense.date" type="date" required />
        <button type="submit">Salvar</button>
        <button @click="cancelEdit">Cancelar</button>
      </form>
    </div>

      <h3>Insignias</h3>
      <ul>
        <li v-for="badge in badges" :key="badge.name">
          {{ badge.name }} - {{ badge.description }}
        </li>
      </ul>
      <h3>Bordas</h3>
      <ul>
        <li v-for="border in borders" :key="border.name">
          {{ border.name }} - {{ border.description }}
        </li>
      </ul>
      <h3>Sugestões</h3>
    <ul>
      <li v-for="suggestion in suggestions" :key="suggestion">
        {{ suggestion }}
      </li>
    </ul>
      
      <button @click="goBack">Voltar ao Dashboard</button>
    </div>
  </template>
  
  <script>
import axios from 'axios';
import { Chart } from 'chart.js/auto';
import { nextTick } from 'vue';

export default {
  data() {
    return {
      user: {},
      gains: [],
      expenses: [],
      categories: [],
      financialScore: { score: 0, saldo: 0 },
      totalGains: 0,
      totalExpenses: 0,
      badges: [
        { name: 'Economista Iniciante', description: 'Gaste menos de 80% dos ganhos (Investido nao conta)' },
        { name: 'Economista Intermediário', description: 'Gaste menos de 70% dos ganhos (Investido nao conta)' },
        { name: 'Economista Avançado', description: 'Gaste menos de 60% dos ganhos (Investido nao conta)' },
        { name: 'Economista Lendário', description: 'Gaste menos de 60% dos ganhos (Investido nao conta)' },
        { name: 'Planejador', description: 'Adicione 5 ganhos de origens diferentes' },
        { name: 'Eita como economiza!', description: 'Poupe pelo menos 20% dos ganhos por 3 meses consecutivos' },
        { name: 'Novo Warren Buffet?', description: 'Invista pela 1º vez (Válido para qualquer valor)' },
        { name: 'Investidor', description: 'Invista pelo menos 10% dos ganhos por 3 meses consecutivos' },
        { name: 'Investidor Iniciante', description: 'Invista pelo menos 20% dos ganhos por 3 meses consecutivos' },
        { name: 'Investidor de Elite', description: 'Invista pelo menos 30% dos ganhos por 3 meses consecutivos' },
        { name: 'Investidor Lendário', description: 'Invista pelo menos 40% dos ganhos por 3 meses consecutivos' },
        { name: 'Investidor Fabuloso', description: 'Invista pelo menos 50% dos ganhos por 3 meses consecutivos' },
        { name: 'Investidor Mítico', description: 'Invista pelo menos 60% dos ganhos por 3 meses consecutivos' },
        { name: 'Investidor Divino', description: 'Invista pelo menos 70% dos ganhos por 3 meses consecutivos' },
        { name: 'Investidor Cósmico', description: 'Invista pelo menos 80% dos ganhos por 3 meses consecutivos' },
        { name: 'Investidor Supremo', description: 'Invista pelo menos 90% dos ganhos por 3 meses consecutivos' },
        { name: 'Investidor Lendário', description: 'Invista 100% dos ganhos por 3 meses consecutivos' }
      ],
      borders: [
        { name: 'Sem Borda', description: 'Score abaixo de 5%' },
        { name: 'Borda Vermelha', description: 'Score entre 5% e 10%' },
        { name: 'Borda Amarela', description: 'Score entre 11% e 20%' },
        { name: 'Borda Azul', description: 'Score entre 21% e 30%' },
        { name: 'Borda Verde', description: 'Score entre 31% e 40%' },
        { name: 'Borda Bronze', description: 'Score entre 41% e 50%' },
        { name: 'Borda Prata', description: 'Score entre 51% e 60%' },
        { name: 'Borda Dourada', description: 'Score entre 61% e 70%' },
        { name: 'Borda Platina', description: 'Score entre 71% e 80%' },
        { name: 'Borda Diamante', description: 'Score entre 81% e 90%' },
        { name: 'Borda Esmeralda', description: 'Score entre 91% e 99%' },
        { name: 'Borda Rubi', description: 'Score 100%' }
      ],
      suggestions: [],
      chartInstance: null,
      newGain: { description: '', amount: 0, source: '', date: '' },
      newExpense: { description: '', amount: 0, category_id: 1, date: '' },
      editingGain: null,
      editingExpense: null
    };
  },
  methods: {
    getHeaders() {
      const token = localStorage.getItem('token');
      console.log('Enviando token no cabeçalho:', token);
      return token ? { Authorization: token } : {};
    },
    async fetchData() {
      try {
        const userId = this.$route.params.id;
        console.log('User ID da rota:', userId);

        // Carregar dados do usuário
        const userResponse = await axios.get('http://localhost:5000/api/users', { headers: this.getHeaders() });
        console.log('Resposta de /api/users:', userResponse.data);
        if (userResponse.data.length > 0) {
          this.user = userResponse.data.find(u => u.id == userId) || userResponse.data[0];

          // Carregar ganhos
          const gainsResponse = await axios.get(`http://localhost:5000/api/gains/${this.user.id}`, { headers: this.getHeaders() });
          this.gains = gainsResponse.data;
          console.log('Ganhos carregados:', this.gains);

          // Carregar despesas
          const expensesResponse = await axios.get(`http://localhost:5000/api/expenses/${this.user.id}`, { headers: this.getHeaders() });
          this.expenses = expensesResponse.data;
          console.log('Expenses carregados:', this.expenses);

          // Carregar categorias
          const categoriesResponse = await axios.get('http://localhost:5000/api/categories', { headers: this.getHeaders() });
          this.categories = categoriesResponse.data;
          console.log('Categories carregados:', this.categories);

          // Calcular o saldo e o score
          this.totalGains = this.gains.reduce((sum, gain) => sum + gain.amount, 0);
          this.totalExpenses = this.expenses.reduce((sum, expense) => sum + expense.amount, 0);
          this.financialScore.saldo = this.totalGains - this.totalExpenses;

          // Cálculo do score
          this.financialScore.score = this.totalGains > 0
            ? ((this.financialScore.saldo / this.totalGains) * 100)
            : 0;

          // Atualizar sugestões
          this.updateSuggestions();

          // Garantir que os dados estão carregados antes de criar o gráfico
          if (this.expenses.length > 0 && this.categories.length > 0) {
            await nextTick();
            this.createChart();
          } else {
            console.log('Dados insuficientes para criar o gráfico');
          }
        } else {
          console.log('Nenhum usuário encontrado');
          this.user = { name: 'Usuário não encontrado' };
        }
      } catch (error) {
        console.error('Erro ao carregar dados:', error);
        this.user = { name: 'Erro ao carregar' };
        this.financialScore = { score: 0, saldo: 0 };
        this.totalGains = 0;
        this.totalExpenses = 0;
      }
    },
    updateSuggestions() {
      if (this.financialScore.score < 30) {
        this.suggestions = ['Considere reduzir suas despesas!', 'Crie um orçamento mensal.'];
      } else if (this.financialScore.score < 70) {
        this.suggestions = ['Bom trabalho! Tente poupar mais 10%.', 'Revise suas categorias de gastos.'];
      } else {
        this.suggestions = ['Excelente! Considere investir seu saldo.', 'Mantenha o controle atual!'];
      }
    },
    createChart() {
      console.log('Entrando no createChart');
      const ctx = this.$refs.chart.getContext('2d');
      console.log('Contexto do canvas:', ctx);
      if (this.chartInstance) {
        this.chartInstance.destroy();
        console.log('Instância anterior destruída');
      }

      // Verificar se temos despesas e categorias
      if (!this.categories || this.categories.length === 0) {
        console.log('Nenhuma categoria disponível');
        return;
      }
      if (!this.expenses || this.expenses.length === 0) {
        console.log('Nenhuma despesa disponível');
        return;
      }

      // Inicializar os valores das categorias como 0
      const expenseByCategory = {};
      this.categories.forEach(category => {
        expenseByCategory[category.id] = 0;
        console.log(`Inicializando categoria ${category.name} (ID ${category.id}) com 0`);
      });

      // Somar os valores das despesas por category_id
      this.expenses.forEach(expense => {
        if (expenseByCategory[expense.category_id] !== undefined) {
          expenseByCategory[expense.category_id] += expense.amount;
          console.log(`Adicionando R$${expense.amount} à categoria ID ${expense.category_id}`);
        } else {
          console.log(`Categoria ID ${expense.category_id} não encontrada para despesa:`, expense);
        }
      });

      // Preparar os dados pro gráfico
      const labels = [];
      const data = [];
      this.categories.forEach(category => {
        if (expenseByCategory[category.id] > 0) {
          labels.push(category.name);
          data.push(expenseByCategory[category.id]);
          console.log(`Adicionando ao gráfico: ${category.name} - R$${expenseByCategory[category.id]}`);
        }
      });

      console.log('Labels finais:', labels);
      console.log('Dados finais:', data);

      if (labels.length === 0 || data.length === 0) {
        console.log('Nenhum dado para exibir no gráfico');
        return;
      }

      const colors = [
        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
        '#FF9F40', '#66BB6A', '#EF5350', '#26C6DA', '#AB47BC', '#D4E157'
      ];

      this.chartInstance = new Chart(ctx, {
        type: 'pie',
        data: {
          labels: labels,
          datasets: [{
            data: data,
            backgroundColor: colors.slice(0, labels.length)
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false
        }
      });
      console.log('Gráfico criado com sucesso');
    },
    getCategoryName(categoryId) {
      const category = this.categories.find(c => c.id === categoryId);
      return category ? category.name : 'Desconhecido';
    },
    async addGain() {
      try {
        const response = await axios.post('http://localhost:5000/api/gains', {
          user_id: this.user.id,
          description: this.newGain.description,
          amount: this.newGain.amount,
          source: this.newGain.source,
          date: this.newGain.date
        }, { headers: this.getHeaders() });
        this.gains.push(response.data);
        this.newGain = { description: '', amount: 0, source: '', date: '' };
        this.fetchData(); // Recarregar dados pra atualizar o gráfico e totais
      } catch (error) {
        console.error('Erro ao adicionar ganho:', error);
        alert('Erro ao adicionar ganho');
      }
    },
    async addExpense() {
      try {
        const response = await axios.post('http://localhost:5000/api/expenses', {
          user_id: this.user.id,
          description: this.newExpense.description,
          amount: this.newExpense.amount,
          category_id: this.newExpense.category_id,
          date: this.newExpense.date
        }, { headers: this.getHeaders() });
        this.expenses.push(response.data);
        this.newExpense = { description: '', amount: 0, category_id: 1, date: '' };
        this.fetchData(); // Recarregar dados
      } catch (error) {
        console.error('Erro ao adicionar despesa:', error);
        alert('Erro ao adicionar despesa');
      }
    },
    editGain(gain) {
      this.editingGain = { ...gain };
    },
    async updateGain() {
      try {
        await axios.put(`http://localhost:5000/api/gains/${this.editingGain.id}`, this.editingGain, { headers: this.getHeaders() });
        this.editingGain = null;
        this.fetchData();
      } catch (error) {
        console.error('Erro ao atualizar ganho:', error);
        alert('Erro ao atualizar ganho');
      }
    },
    cancelEdit() {
      this.editingGain = null;
      this.editingExpense = null;
    },
    async deleteGain(gainId) {
      if (!gainId) {
        console.error('ID do ganho inválido:', gainId);
        alert('Erro: ID do ganho inválido');
        return;
      }
      if (confirm('Tem certeza que deseja deletar este ganho?')) {
        try {
          await axios.delete(`http://localhost:5000/api/gains/${gainId}`, { headers: this.getHeaders() });
          this.gains = this.gains.filter(g => g.id !== gainId);
          this.fetchData();
        } catch (error) {
          console.error('Erro ao deletar ganho:', error);
          alert('Erro ao deletar ganho');
        }
      }
    },
    editExpense(expense) {
      this.editingExpense = { ...expense };
    },
    async updateExpense() {
      try {
        await axios.put(`http://localhost:5000/api/expenses/${this.editingExpense.id}`, this.editingExpense, { headers: this.getHeaders() });
        this.editingExpense = null;
        this.fetchData();
      } catch (error) {
        console.error('Erro ao atualizar despesa:', error);
        alert('Erro ao atualizar despesa');
      }
    },
    async deleteExpense(expenseId) {
      if (confirm('Tem certeza que deseja deletar esta despesa?')) {
        try {
          await axios.delete(`http://localhost:5000/api/expenses/${expenseId}`, { headers: this.getHeaders() });
          this.expenses = this.expenses.filter(e => e.id !== expenseId);
          this.fetchData();
        } catch (error) {
          console.error('Erro ao deletar despesa:', error);
          alert('Erro ao deletar despesa');
        }
      }
    },
    goBack() {
      this.$router.push('/');
    }
  },
  mounted() {
    this.fetchData();
  },
  beforeUnmount() {
    if (this.chartInstance) {
      this.chartInstance.destroy();
    }
  }
};
</script>

<style>
.profile-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

h1 {
  color: #2c3e50;
  text-align: center;
  margin-bottom: 20px;
}

h2 {
  color: #42b983;
  font-size: 24px;
  text-align: center;
  margin-bottom: 10px;
}

p {
  color: #34495e;
  font-size: 16px;
  margin: 5px 0;
}

h3 {
  color: #2c3e50;
  margin-top: 20px;
  border-bottom: 1px solid #ddd;
  padding-bottom: 5px;
}

ul {
  list-style-type: none;
  padding: 0;
}

li {
  background-color: #fff;
  margin: 5px 0;
  padding: 10px;
  border-left: 4px solid #42b983;
  border-radius: 4px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

form {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

input, select{
  padding: 8px;
  border-radius: 4px;
  border: 1px solid #ddd;
}

button {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 10px 20px;
  cursor: pointer;
  border-radius: 5px;
  margin-top: 20px;
  display: block;
  margin-left: auto;
  margin-right: auto;
}

button:hover {
  background-color: #2980b9;
}
</style>