<template>
  <div>
    <h1>Bem-vindo, {{ user.name || 'Usuário' }}!</h1>
    <router-link to="/profile" class="score-link">Veja seu Score</router-link>

    <h3>Adicionar Ganho</h3>
    <form @submit.prevent="addGain">
      <input v-model="newGain.description" placeholder="Descrição" required />
      <input v-model.number="newGain.amount" type="number" placeholder="Valor" required />
      <input v-model="newGain.source" placeholder="Fonte" required />
      <input v-model="newGain.date" type="date" required />
      <button type="submit">Adicionar Ganho</button>
    </form>

    <h2>Seus Ganhos</h2>
    <ul>
      <li v-for="gain in gains" :key="gain.description">
        {{ gain.description }} - R${{ gain.amount }} ({{ gain.source }}, {{ gain.date }})
      </li>
      <li v-if="!gains.length">Nenhum ganho encontrado.</li>
    </ul>

    <h3>Adicionar Despesa</h3>
    <form @submit.prevent="addExpense">
      <input v-model="newExpense.description" placeholder="Descrição" required />
      <input v-model.number="newExpense.amount" type="number" placeholder="Valor" required />
      <input v-model="newExpense.date" type="date" required />
      <select v-model="newExpense.category_id" required>
        <option disabled value="">Selecione uma categoria</option>
        <option v-for="category in categories" :key="category.id" :value="category.id">
          {{ category.name }}
        </option>
      </select>
      <button type="submit">Adicionar Despesa</button>
    </form>

    <h2>Suas Despesas</h2>
    <ul>
      <li v-for="expense in expenses" :key="expense.description">
        {{ expense.description }} - R${{ expense.amount }} ({{ expense.date }})
      </li>
      <li v-if="!expenses.length">Nenhuma despesa encontrada.</li>
    </ul>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      user: {},
      gains: [],
      expenses: [],
      categories: [],
      newGain: {
        description: '',
        amount: null,
        source: '',
        date: ''
      },
      newExpense: {
        description: '',
        amount: null,
        date: '',
        category_id: ''
      }
    };
  },
  methods: {
    async fetchData() {
      try {
        const userResponse = await axios.get('http://localhost:5000/api/users');
        console.log('Resposta do /api/users:', userResponse.data);
        if (userResponse.data.length > 0) {
          this.user = userResponse.data[0];
          const gainsResponse = await axios.get(`http://localhost:5000/api/gains/${this.user.id}`);
          console.log('Resposta do /api/gains:', gainsResponse.data);
          this.gains = gainsResponse.data;
          const expensesResponse = await axios.get(`http://localhost:5000/api/expenses/${this.user.id}`);
          console.log('Resposta do /api/expenses:', expensesResponse.data);
          this.expenses = expensesResponse.data;
        } else {
          console.log('Nenhum usuário encontrado.');
        }
      } catch (error) {
        console.error('Erro ao carregar dados:', error);
        this.user = { name: 'Erro ao carregar' };
        this.gains = [];
        this.expenses = [];
      }
    },
    async addGain() {
      try {
        const payload = {
          user_id: this.user.id,
          description: this.newGain.description,
          amount: this.newGain.amount,
          source: this.newGain.source,
          date: this.newGain.date
        };
        const response = await axios.post('http://localhost:5000/api/gains', payload);
        console.log('Ganho adicionado:', response.data);
        this.newGain = { description: '', amount: null, source: '', date: '' };
        await this.fetchData();
      } catch (error) {
        console.error('Erro ao adicionar ganho:', error);
      }
    },
    async addExpense() {
      try {
        const payload = {
          user_id: this.user.id,
          category_id: this.newExpense.category_id,
          amount: this.newExpense.amount,
          description: this.newExpense.description,
          date: this.newExpense.date
        };
        const response = await axios.post('http://localhost:5000/api/expenses', payload);
        console.log('Despesa adicionada:', response.data);
        this.newExpense = { description: '', amount: null, date: '', category_id: '' };
        await this.fetchData();
      } catch (error) {
        console.error('Erro ao adicionar despesa:', error);
      }
    },
    async fetchCategories() {
      try {
        const response = await axios.get('http://localhost:5000/api/categories');
        console.log('Resposta do /api/categories:', response.data);
        this.categories = response.data;
      } catch (error) {
        console.error('Erro ao carregar categorias:', error);
      }
    }
  },
  mounted() {
    this.fetchCategories();
    this.fetchData();
  }
};
</script>

<style>
h1 { color: #2c3e50; }
h2 { color: #42b983; }
h3 { color: #2c3e50; }
ul { list-style-type: none; }
form { margin: 20px 0; }
input, select, button { margin: 5px; padding: 5px; }
button { background-color: #42b983; color: white; border: none; padding: 8px 16px; cursor: pointer; }
button:hover { background-color: #369a74; }
.score-link { 
  display: inline-block; 
  margin: 10px 0; 
  padding: 8px 16px; 
  background-color: #3498db; 
  color: white; 
  text-decoration: none; 
  border-radius: 5px; 
}
.score-link:hover { background-color: #2980b9; }
</style>